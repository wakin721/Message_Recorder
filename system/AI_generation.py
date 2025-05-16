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
            reply = deleteByStartAndEnd(reply.content, <think>, </think>)            
            return reply

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

    def deleteByStartAndEnd(s, start, end):
        # 找出两个字符串在原始字符串中的位置，开始位置是：开始始字符串的最左边第一个位置，结束位置是：结束字符串的最右边的第一个位置
        x1 = s.index(start)
        x2 = s.index(end) + len(end)  # s.index()函数算出来的是字符串的最左边的第一个位置
        # 找出两个字符串之间的内容
        x3 = s[x1:x2]
        # 将内容替换为控制符串
        result = s.replace(x3, "")
        return result



