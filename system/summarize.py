from pkg.platform.types import *
from pkg.provider.entities import Message
import os
import json
import datetime
import time
from plugins.Message_Recorder.system.AI_generation import ai_generation
import asyncio

class Summarize:
    def __init__(self, msg, model, user_name, assistant_name, event_id, summarize_lens, ap):
        self.msg = msg
        self.message = None
        self.dates = None
        self.model = model
        self.user_name = user_name
        self.assistant_name = assistant_name
        self.event_id = event_id
        self.summarize_lens = summarize_lens
        self.ap = ap

    async def summarize(self):

        if len(self.message) < 3:
            print("对话过少无法生成总结")
            return

        data_folder = f"{os.getcwd()}\\data\\plugins\\Message_Recorder\\data"

        temp_list = str(self.message)
        temp_list = temp_list.replace("user", self.user_name)
        temp_list = temp_list.replace("assistant", self.assistant_name)

        temp_input = f"请总结以下对话的主要内容：\n{temp_list}\n总结要求：\n1. 长度控制在{str(self.summarize_lens)}字以内\n2. 保留重要的事实和情感\n3. 使用第三人称叙述\n4. 时态使用过去式"

        async def ai_reply(temp_list, model):
            summarize = ai_generation(self.ap)
            reply = await summarize.generate_reply([Message(role="user", content=temp_list)], model)
            return reply

        try:
            reply = await asyncio.wait_for(ai_reply(temp_input, self.model), timeout=20)
            try:  # 若有json文件则打开
                with open(f"{data_folder}\\person_{str(self.event_id)}_summarize.json", "r", encoding="utf-8") as f:
                    summarize = json.load(f)
                    try:
                        summarize[self.dates[0]] += reply
                    except:
                        summarize[self.dates[0]] = reply

                if len(summarize[self.dates[0]]) > 500:
                    temp_input = f"请总结以下对话的主要内容：\n{summarize[self.dates[0]]}\n总结要求：\n1. 长度控制在{str(self.summarize_lens)}字以内\n2. 保留重要的事实和情感\n3. 使用第三人称叙述\n4. 时态使用过去式"

                    async def ai_reply(temp_input, model):
                        summarize = ai_generation(self.ap)
                        summarize_temp = await summarize.generate_reply([Message(role="user", content=temp_input)],
                                                                        model)
                        return summarize_temp

                    try:
                        summarize_temp = await asyncio.wait_for(
                            ai_reply(temp_input, self.model), timeout=20)
                        summarize[self.dates[0]] = summarize_temp

                    except asyncio.TimeoutError:
                        print("\n=== 总结生成超时 ===")
                        return

                    print(f"生成的总结:{summarize_temp}")
                    print("\n=== 总结已更新 ===")
                else:
                    print(f"生成的总结:{reply}")
                    print("\n=== 总结已更新 ===")

                with open(f"{data_folder}\\person_{str(self.event_id)}_summarize.json", 'w',
                          encoding="utf-8") as f:  # 保存记录
                    json_str = json.dumps(summarize, ensure_ascii=False)
                    f.write(json_str)
                print("\n=== 保存成功 ===")
                print(f"总结保存地点：{data_folder}\\person_{str(self.event_id)}_summarize.json")

            except:  # 若无json文件则生成
                summarize = {self.dates[0]: reply}
                with open(f"{data_folder}\\person_{str(self.event_id)}_summarize.json", 'w',
                          encoding="utf-8") as f:  # 保存记录
                    json_str = json.dumps(summarize, ensure_ascii=False)
                    f.write(json_str)
            print(f"生成的总结:{reply}")
            print("\n=== 保存成功 ===")
            print(f"总结保存地点：{data_folder}\\person_{str(self.event_id)}_summarize.json")




        except asyncio.TimeoutError:
            print("\n=== 总结生成超时 ===")
            return

    async def summarize_memory(self):
        self.dates = list(self.msg.keys())
        while True:
            if len(self.dates) > 1:
                print(f"=== 正在生成{self.dates[0]}的总结 ===")
                self.message = self.msg[self.dates[0]]
                await self.summarize()
                del self.msg[self.dates[0]]
                self.dates = list(self.msg.keys())

            else:
                print(f"=== 正在生成{self.dates[0]}的总结 ===")
                self.message = self.msg[self.dates[0]]
                await self.summarize()

                message_ = {}
                message_[self.dates[0]] = self.msg[self.dates[0]][-2:]
                print(message_)

                temp_folder = f"{os.getcwd()}\\data\\plugins\\Message_Recorder\\temp"
                with open(f"{temp_folder}\\person_{str(self.event_id)}_temp.json", 'w', encoding="utf-8") as f:  # 保存记录
                    json_str = json.dumps(message_, ensure_ascii=False)
                    f.write(json_str)
                print("\n=== 已删除临时对话 ===")

                return








