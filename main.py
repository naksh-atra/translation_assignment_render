# from livekit import agents
# from livekit.agents import AgentSession, Agent, RoomInputOptions
# from livekit.plugins import (
#     openai,
#     cartesia,
#     deepgram,
#     noise_cancellation,
#     silero,
# )
# from livekit.plugins.turn_detector.multilingual import MultilingualModel

# from dotenv import load_dotenv
# load_dotenv(dotenv_path=".env.local")



# class Translator(Agent):
#     def __init__(self) -> None:
#         super().__init__(instructions= "Translate English speech to Hindi only, say nothing else",)

# async def entrypoint(ctx: agents.JobContext):
#     session = AgentSession(
        
#             stt=deepgram.STT(),
#             llm=openai.LLM(model="gpt-4o-mini"),
#             tts=cartesia.TTS(
#                 model="sonic-2",
#                 voice="28ca2041-5dda-42df-8123-f58ea9c3da00",
#                 language="hi"
#             ),
#             vad=silero.VAD.load(),
#         turn_detection=MultilingualModel(),
#         use_tts_aligned_transcription=True,
#     )

#     await session.start(
#         room=ctx.room,
#         agent=Translator(),
#         room_input_options=RoomInputOptions(
#             noise_cancellation=noise_cancellation.BVC(), 
#         ),
#     )

#     await ctx.connect()

#     await session.generate_reply(
#         instructions="Greet 'Hello I'm a translator'"
#     )


# if __name__ == "__main__":
#     agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))


# from dotenv import load_dotenv
# import logging
# from typing import AsyncIterable, Optional

# from livekit import agents, rtc
# from livekit.agents import AgentSession, Agent, RoomInputOptions, ModelSettings, stt, llm
# from livekit.plugins import (
#     openai,
#     cartesia,
#     deepgram,
#     noise_cancellation,
#     silero,
# )
# from livekit.plugins.turn_detector.multilingual import MultilingualModel

# load_dotenv(dotenv_path=".env.local")

# # Enable logging for transcription debugging
# logging.basicConfig(level=logging.INFO)


# class Translator(Agent):
#     def __init__(self) -> None:
#         super().__init__(
#             instructions="Translate English speech to Hindi only, say nothing else",
#         )

#     # ======== STT transcripts (User speech) ========
#     async def stt_node(
#         self, audio: AsyncIterable[rtc.AudioFrame], model_settings: ModelSettings
#     ) -> Optional[AsyncIterable[stt.SpeechEvent]]:
#         async for event in Agent.default.stt_node(self, audio, model_settings):
#             if isinstance(event, stt.SpeechEvent) and event.type == "final_transcript":
#                 text = event.text
#                 logging.info(f"[STT Transcript] User: {text}")
#                 # send to frontend over data channel
#                 await self.session.send_data(f"USER_TRANSCRIPT::{text}".encode(), reliable=True)
#             yield event

#     # ======== TTS transcripts (Assistant speech) ========
#     async def llm_node(
#         self,
#         chat_ctx: llm.ChatContext,
#         tools: list[llm.FunctionTool],
#         model_settings: ModelSettings
#     ) -> AsyncIterable[llm.ChatChunk]:
#         async for chunk in Agent.default.llm_node(self, chat_ctx, tools, model_settings):
#             if chunk.text:
#                 logging.info(f"[TTS Transcript] Assistant: {chunk.text}")
#                 # send to frontend over data channel
#                 await self.session.send_data(f"ASSISTANT_TRANSCRIPT::{chunk.text}".encode(), reliable=True)
#             yield chunk


# async def entrypoint(ctx: agents.JobContext):
#     session = AgentSession(
#         stt=deepgram.STT(),
#         llm=openai.LLM(model="gpt-4o-mini"),
#         tts=cartesia.TTS(
#             model="sonic-2",
#             voice="28ca2041-5dda-42df-8123-f58ea9c3da00",
#             language="hi"
#         ),
#         vad=silero.VAD.load(),
#         turn_detection=MultilingualModel(),
#     )

#     await session.start(
#         room=ctx.room,
#         agent=Translator(),
#         room_input_options=RoomInputOptions(
#             noise_cancellation=noise_cancellation.BVC(),
#         ),
#         room_output_options=RoomOutputOptions(sync_transcription=True)
#     )

#     await ctx.connect()

#     await session.generate_reply(
#         instructions="Greet 'Hello I'm a translator'"
#     )


# if __name__ == "__main__":
#     agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))




from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, RoomOutputOptions
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import UserInputTranscribedEvent

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env.local")


class Translator(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="Translate English speech to Hindi only, say nothing else"
        )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(
            model="sonic-2",
            voice="28ca2041-5dda-42df-8123-f58ea9c3da00",
            language="hi"
        ),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
        use_tts_aligned_transcript=True,  # enables TTS-aligned transcription for realtime sync
    )
    
    
    # @session.event("conversation_item_added")
    # async def on_conversation_item_added(item):
    #     print(f"[BACKEND] Conversation item added: {item}")
    
    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event: UserInputTranscribedEvent):
        print(f"User input transcribed: {event.transcript}, final: {event.is_final}, speaker id: {event.speaker_id}")


    await session.start(
        room=ctx.room,
        agent=Translator(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
        room_output_options=RoomOutputOptions(
            transcription_enabled=True,  # ensure STT transcriptions are forwarded
            sync_transcription=True       # word-by-word sync with speech
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions="Greet 'Hello I'm a translator'"
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
