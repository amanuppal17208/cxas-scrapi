import json
import logging
import os
import sys
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

import certifi
import websocket
from google.cloud import ces_v1beta
from google.protobuf import json_format

from cxas_scrapi.core.audio_transformer import AudioTransformer
from cxas_scrapi.core.sessions import Sessions, Modality, AgentTurnManager, BIDI_SESSION_URI, AUDIO_CHUNK_SIZE, CHUNK_DELAY, SILENCE_PADDING_CHUNKS
from cxas_scrapi.evals.simulation_evals import SimulationEvals, LLMUserConversation, StepStatus, ExpectationStatus, SimulationReport
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContinuousBidiSessionHandler:
    def __init__(self, location: str, token: str, config: Dict[str, Any], eval_conv: LLMUserConversation, audio_transformer: AudioTransformer, creds: Any, project_id: str):
        self.uri = BIDI_SESSION_URI + location
        self.token = token
        self.config = config
        self.eval_conv = eval_conv
        self.audio_transformer = audio_transformer
        self.creds = creds
        self.project_id = project_id
        self.agent_turn_manager = AgentTurnManager()
        self.ws_app = None
        self.outputs = []
        self.conversation_finished = False
        self.accumulated_agent_text = ""
        self.lock = threading.Lock()

    def _send_silence(self, num_chunks: int):
        silence_chunk = b"\x00" * AUDIO_CHUNK_SIZE
        for _ in range(num_chunks):
            query_message = ces_v1beta.BidiSessionClientMessage(
                realtime_input=ces_v1beta.SessionInput(audio=silence_chunk)
            )
            query_json = json_format.MessageToJson(
                query_message._pb,
                preserving_proto_field_name=False,
                indent=None,
            )
            self.ws_app.send(query_json)
            time.sleep(CHUNK_DELAY)

    def _send_audio_message(self, audio_bytes: bytes, variables: Dict[str, Any], turn_index: int):
        logger.info(f"Sending leading silence before turn {turn_index}...")
        self._send_silence(SILENCE_PADDING_CHUNKS)

        logger.info(f"Sending audio chunks for turn {turn_index}...")
        for i in range(0, len(audio_bytes), AUDIO_CHUNK_SIZE):
            chunk = audio_bytes[i : i + AUDIO_CHUNK_SIZE]
            input_args = {"audio": chunk}
            if i == 0 and variables:
                input_args["variables"] = variables

            query_message = ces_v1beta.BidiSessionClientMessage(
                realtime_input=ces_v1beta.SessionInput(**input_args)
            )
            query_json = json_format.MessageToJson(
                query_message._pb,
                preserving_proto_field_name=False,
                indent=None,
            )
            self.ws_app.send(query_json)
            time.sleep(CHUNK_DELAY)

        logger.info(f"Sending trailing silence for turn {turn_index} to trigger endpointing...")
        self._send_silence(SILENCE_PADDING_CHUNKS)

        logger.info(f"Waiting for agent to finish turn {turn_index}...")
        while not self.agent_turn_manager.is_agent_done_talking():
            self._send_silence(1)

        self.agent_turn_manager.reset()
        time.sleep(1)

    def _send_inputs(self):
        try:
            logger.info("Sending config...")
            config_message = ces_v1beta.BidiSessionClientMessage(
                config=ces_v1beta.SessionConfig(
                    session=self.config["session"],
                    input_audio_config=self.config.get("input_audio_config"),
                    output_audio_config=self.config.get("output_audio_config"),
                    use_tool_fakes=self.config.get("use_tool_fakes", False),
                )
            )
            config_json = json_format.MessageToJson(
                config_message._pb,
                preserving_proto_field_name=False,
                indent=None,
            )
            self.ws_app.send(config_json)

            # Initial turn
            user_utterance, variables = self.eval_conv.next_user_utterance()
            logger.info(f"First User Utterance: {user_utterance}")
            
            idx = 0
            while user_utterance:
                if user_utterance.startswith("event:"):
                    event_name = user_utterance.removeprefix("event:").strip()
                    logger.info(f"Sending event: {event_name}")
                    event_payload = {"event": {"event": event_name}}
                    if variables:
                        event_payload["event"]["variables"] = variables
                    
                    session_input_pb = ces_v1beta.SessionInput()._pb
                    json_format.ParseDict(
                        event_payload,
                        session_input_pb,
                        ignore_unknown_fields=False,
                    )
                    session_input = ces_v1beta.SessionInput(session_input_pb)

                    query_message = ces_v1beta.BidiSessionClientMessage(
                        realtime_input=session_input
                    )
                    query_json = json_format.MessageToJson(
                        query_message._pb,
                        preserving_proto_field_name=False,
                        indent=None,
                    )
                    self.ws_app.send(query_json)
                    
                    # Wait for agent to finish turn
                    while not self.agent_turn_manager.is_agent_done_talking():
                        time.sleep(1)
                    self.agent_turn_manager.reset()
                    
                    # Get accumulated text
                    with self.lock:
                        agent_text = self.accumulated_agent_text
                        self.accumulated_agent_text = ""
                    
                    # Generate next user utterance
                    user_utterance, variables = self.eval_conv.next_user_utterance(agent_text)
                    logger.info(f"Next User Utterance after event: {user_utterance}")
                    idx += 1
                    continue

                if user_utterance.startswith("dtmf:"):
                    dtmf_digits = user_utterance.removeprefix("dtmf:").strip()
                    logger.info(f"Sending DTMF: {dtmf_digits}")
                    dtmf_payload = {"dtmf": dtmf_digits}
                    
                    session_input_pb = ces_v1beta.SessionInput()._pb
                    json_format.ParseDict(
                        dtmf_payload,
                        session_input_pb,
                        ignore_unknown_fields=False,
                    )
                    session_input = ces_v1beta.SessionInput(session_input_pb)

                    query_message = ces_v1beta.BidiSessionClientMessage(
                        realtime_input=session_input
                    )
                    query_json = json_format.MessageToJson(
                        query_message._pb,
                        preserving_proto_field_name=False,
                        indent=None,
                    )
                    self.ws_app.send(query_json)
                    
                    # Wait for agent to finish turn
                    while not self.agent_turn_manager.is_agent_done_talking():
                        time.sleep(1)
                    self.agent_turn_manager.reset()
                    
                    # Get accumulated text
                    with self.lock:
                        agent_text = self.accumulated_agent_text
                        self.accumulated_agent_text = ""
                    
                    # Generate next user utterance
                    user_utterance, variables = self.eval_conv.next_user_utterance(agent_text)
                    logger.info(f"Next User Utterance after DTMF: {user_utterance}")
                    idx += 1
                    continue
                
                # Convert text to speech
                logger.info(f"Converting text to speech: {user_utterance}")
                tts_result = self.audio_transformer.text_to_speech_bytes(
                    text=user_utterance,
                    credentials=self.creds,
                    project_id=self.project_id,
                )
                audio_bytes = tts_result["audio_bytes"]
                
                self._send_audio_message(audio_bytes, variables, idx)
                
                # Get accumulated text and reset for next turn
                with self.lock:
                    agent_text = self.accumulated_agent_text
                    self.accumulated_agent_text = ""
                
                logger.info(f"Agent Response received: {agent_text}")
                
                # Generate next user utterance
                user_utterance, variables = self.eval_conv.next_user_utterance(agent_text)
                logger.info(f"Next User Utterance: {user_utterance}")
                idx += 1

            logger.info("Conversation finished.")
            self.conversation_finished = True
            self.ws_app.close()

        except Exception as e:
            logger.error(f"Error during send_inputs: {e}")
            if self.ws_app:
                self.ws_app.close()

    def _on_open(self, ws):
        logger.info("WebSocket connection opened")
        threading.Thread(target=self._send_inputs, daemon=True).start()

    def _on_message(self, ws, message):
        try:
            response_pb = ces_v1beta.BidiSessionServerMessage()._pb
            json_format.Parse(message, response_pb, ignore_unknown_fields=True)
            response = ces_v1beta.BidiSessionServerMessage(response_pb)

            if response.session_output:
                self.outputs.append(response.session_output)

                if response.session_output.audio:
                    self.agent_turn_manager.add_audio(response.session_output.audio)

                if response.session_output.turn_completed:
                    self.agent_turn_manager.mark_turn_completed()

                # Accumulate text response if available
                if hasattr(response.session_output, "text") and response.session_output.text:
                    with self.lock:
                        self.accumulated_agent_text += response.session_output.text + " "

        except Exception as e:
            logger.error(f"Failed to parse message: {e}")

    def _on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")

    def run(self):
        logger.info(f"Connecting to WebSocket: {self.uri}")
        self.ws_app = websocket.WebSocketApp(
            self.uri,
            header={"Authorization": f"Bearer {self.token}"},
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        wst = threading.Thread(
            target=self.ws_app.run_forever,
            kwargs={"sslopt": {"ca_certs": certifi.where()}},
        )
        wst.daemon = True
        wst.start()

        wst.join()
        return ces_v1beta.RunSessionResponse(outputs=self.outputs)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run Continuous Voice Simulations.")
    parser.add_argument("--app-name", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--parallelism", type=int, default=1) # Keep to 1 for now to debug
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--end-index", type=int, default=10)
    args = parser.parse_args()

    sim_evals = SimulationEvals(args.app_name)
    audio_transformer = AudioTransformer()
    
    evals_dir = os.path.join(args.output_dir, 'sim_evals')
    files = sorted([f for f in os.listdir(evals_dir) if f.endswith(".json")])
    files_to_run = files[args.start_index:args.end_index]

    results_list = []

    for item in files_to_run:
        json_path = os.path.join(evals_dir, item)
        with open(json_path, "r") as f:
            test_case = json.load(f)

        session_id = str(uuid.uuid4())
        eval_conv = LLMUserConversation(
            genai_client=sim_evals.genai_client,
            genai_model="gemini-3.1-flash-lite-preview",
            test_case=test_case,
        )

        config = {
            "session": f"{args.app_name}/sessions/{session_id}",
            "input_audio_config": ces_v1beta.InputAudioConfig(
                audio_encoding=ces_v1beta.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
            ),
            "output_audio_config": ces_v1beta.OutputAudioConfig(
                audio_encoding=ces_v1beta.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
            ),
        }

        logger.info(f"Running voice simulation for: {item}")
        logger.info(f"Conv ID / Session ID: {session_id}") # Logged here
        
        handler = ContinuousBidiSessionHandler(
            location=sim_evals.location,
            token=sim_evals.sessions_client.token,
            config=config,
            eval_conv=eval_conv,
            audio_transformer=audio_transformer,
            creds=sim_evals.creds,
            project_id=sim_evals.project_id
        )
        
        try:
            response = handler.run()
            
            # Evaluate expectations after conversation completes
            detailed_trace = eval_conv.get_transcript().splitlines()
            
            sim_evals._evaluate_expectations(eval_conv, detailed_trace, "gemini-3.1-flash-lite-preview", True)
            
            report = eval_conv.generate_report()
            
            all_goals_completed = all(report.goals_df['status'] == 'Completed')
            all_expectations_met = True
            if report.expectations_df is not None:
                all_expectations_met = all(report.expectations_df['status'] == 'Met')
            
            passed = all_goals_completed and all_expectations_met
            
            results_list.append({
                "name": item,
                "session_id": session_id,
                "passed": passed,
                "goals_html": report.goals_df.to_html(classes='table', index=False),
                "expectations_html": report.expectations_df.to_html(classes='table', index=False) if report.expectations_df is not None else "",
                "colored_trace": eval_conv.get_transcript() # Fallback to text transcript
            })
            
        except Exception as e:
            logger.error(f"Failed to run {item}: {e}")
            results_list.append({
                "name": item,
                "session_id": session_id,
                "passed": False,
                "goals_html": "<div>Error occurred</div>",
                "expectations_html": "",
                "colored_trace": str(e)
            })

    # Generate HTML report similar to run_evals.py
    html_content = "<html><body><h1>Voice Simulation Results</h1><table><tr><th>Name</th><th>Result</th><th>Conv ID</th></tr>" # Updated header
    for res in results_list:
         status = "Pass" if res['passed'] else "Fail"
         html_content += f"<tr><td>{res['name']}</td><td>{status}</td><td>{res['session_id']}</td></tr>" # Updated row
    html_content += "</table></body></html>"
    
    output_path = os.path.join(args.output_dir, "voice_summary.html")
    with open(output_path, "w") as f:
         f.write(html_content)
    logger.info(f"Generated report at {output_path}")

if __name__ == "__main__":
    main()
