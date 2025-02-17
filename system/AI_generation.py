from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
import asyncio


class ai_generation(BasePlugin):
    def __init__(self, ap,model):
        self.ap = ap
        self.model = model

    async def ai_reply(self,msg_input):
        try:
            model = await self.ap.model_mgr.get_model_by_name(self.ap.provider_cfg.data.get("model", self.model))
            reply = [await model.requester.call(query=None, model=model,messages=msg_input)][0]
            return reply.content

        except Exception as e:
            print(f"AI生成失败: {e}")
            return "AI生成超时"

    async def generate_reply(self,msg_input):
        try:
            reply = await asyncio.wait_for(ai_generation.ai_reply(self,msg_input), timeout=20)
            return reply

        except asyncio.TimeoutError:
            print("\n=== 生成超时 ===")
            return "AI生成超时"



