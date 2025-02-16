from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext


class ai_generation(BasePlugin):
    def __init__(self, ap):
        self.ap = ap

    async def generate_reply(self,msg_input,model):
        try:
            model = await self.ap.model_mgr.get_model_by_name(self.ap.provider_cfg.data.get("model", model))
            reply = [await model.requester.call(query=None, model=model,messages=msg_input)][0]
            return reply.content

        except Exception as e:
            print(f"AI生成失败: {e}")
            return "AI生成超时"



