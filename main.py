from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from pkg.platform.types import *
from pkg.provider.entities import Message
import os
import json
import datetime
import copy
from plugins.Message_Recorder.system.summarize import Summarize
from plugins.Message_Recorder.system.AI_generation import ai_generation

# 注册插件
@register(name="Message_Recorder", description="用于记录聊天记录", version="preview2.3", author="和錦わきん")
class Message_Recorder(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.data_folder = None
        self.temp_folder = None
        self.model = None
        self.user_name = None
        self.assistant_name = None
        self.summarize_lens = None
        self.conversation_num = None
        self.output_num = None


    # 异步初始化
    async def initialize(self):
        folder = f"{os.getcwd()}\\data\\plugins\\Message_Recorder"  # 创建文件夹
        self.data_folder = data_folder = os.path.join(folder, "data")  # 创建data文件夹
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
            print(f"未找到data文件夹，已在“{data_folder}”创建data文件夹")

        self.temp_folder = temp_folder = os.path.join(folder, "temp")  # 创建temp文件夹
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
            print(f"未找到temp文件夹，已在“{temp_folder}”创建temp文件夹")

        card_folder = os.path.join(folder, "card")  # 创建temp文件夹
        if not os.path.exists(card_folder):
            os.makedirs(card_folder)
            print(f"未找到card文件夹，已在“{card_folder}”创建card文件夹")

        try:
            with open(f"{os.getcwd()}\\data\\config\\provider.json", "r", encoding="utf-8") as f:
                content = json.load(f)
                self.model = model = content['model']
        except:
            print(f"未找到模型，请检查“{os.getcwd()} \\data\\config\\provider.json”文件")

        try:
            with open(f"{card_folder}\\card.json", "r", encoding="utf-8") as f:
                information = json.load(f)
                self.system_prompt = system_prompt = information['system_prompt']
                self.user_name = user_name = information["user_name"]
                self.assistant_name = assistant_name = information["assistant_name"]
                self.summarize_lens = int(information["summarize_lens"])
                self.conversation_num = int(information["conversation_num"])
                self.output_num = int(information["output_num"])

        except:
            print(f"未找到card文件，开始生成配置文件")
            print(f"配置文件生成地址：{os.getcwd()}\\data\\scenario\\default.json")

            information = {'system_prompt': '', 'user_name': '', 'assistant_name': '', 'summarize_lens': 150,
                           'conversation_num': 10, 'output_num': 150}

            try:
                with open(f"{os.getcwd()}\\data\\scenario\\default.json", "r", encoding="utf-8") as f:
                    content = json.load(f)
                    self.system_prompt = system_prompt = content['prompt'][0]['content']
                    information["system_prompt"] = system_prompt

                    print(f"已从“{os.getcwd()}\\data\\scenario\\default.json”获取system_prompt文件")

            except:
                print(f"未找到prompt文件，请检查“{os.getcwd()}\\data\\scenario\\default.json”文件")

            user_name = ""
            assistant_name = ""
            self.summarize_lens =  int(information["summarize_lens"])
            self.conversation_num = int(information["conversation_num"])
            self.output_num = int(information["output_num"])

        if user_name == "" or assistant_name == "":
            temp_input = f"请从以下系统提示中提取出对话发起者和对话回答者：\n{system_prompt}\n总结要求：\n1.对话发起者在前，对话回答者在后，之间用英文逗号分隔\n2.总数必须是2个\n3.每个标签必须独立，不能包含换行符\n4. 直接返回标签列表，不要其他解释"

            summarize = ai_generation(self.ap,model)
            name = await summarize.generate_reply([Message(role="user", content=temp_input)])

            name = name.split(",")
            user_name = name[0].replace(" ", "")
            assistant_name = name[1].replace(" ", "")
            self.user_name = information['user_name'] = user_name
            self.assistant_name = information['assistant_name'] = assistant_name
            print(f"人名已提取,user_name={user_name},assistant_name={assistant_name}")
            with open(f"{card_folder}\\card.json", 'w', encoding="utf-8") as f:  # 保存记录
                json_str = json.dumps(information, ensure_ascii=False)
                f.write(json_str)
            print("配置文件已保存")

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):

        Time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 获取时间
        Date = datetime.datetime.now().strftime('%Y-%m-%d')

        try:
            with open(f"{self.data_folder}\\person_{str(ctx.event.sender_id)}_summarize.json", "r", encoding="utf-8") as f:
                summarize = json.load(f)
        except:
            summarize = {}

        try:
            with open(f"{self.temp_folder}\\person_{str(ctx.event.sender_id)}_temp.json", "r", encoding="utf-8") as f:
                msg = json.load(f)

        except:
            msg = {Date:[]}

        msg_user = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象

        if msg_user == "查看总结":
            dates = summarize.keys()
            if len(dates) > 0:
                output = "当前总结：\n"
                for i in dates:
                    output += i + ":\n" + summarize[i] + "\n"
            else:
                output = "当前尚未生成总结"

            print("\n=== 以下为总结内容 ===")
            print(output)
            print("\n=== 以上为总结内容 ===")

            msg_chain = MessageChain([
                # Quote(),
                At(ctx.event.sender_id),
                Plain(output)
            ])
            await ctx.send_message("person", int(ctx.event.launcher_id), msg_chain)

            ctx.prevent_default()  # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_postorder()
            return

        message = []
        dates = list(msg.keys())
        temp_dates = copy.deepcopy(dates)
        while True:
            if len(temp_dates) > 1:
                for i in msg[temp_dates[0]]:
                    message.append(i)
                temp_dates.pop(0)
            else:
                for i in msg[temp_dates[0]]:
                    message.append(i)
                break

        message.insert(0, {"role": "system",
                           "content": f"{self.system_prompt}\n以下是先前对话的总结：{summarize}\n请根据以上信息作出符合{self.assistant_name}角色设定的回复，确保回复充分体现{self.assistant_name}的性格特征和情感反应。回复字数不超过{self.output_num}字。"})

        message.append({"role": "user", "content": '[' + Time + ']' + msg_user})  # 修饰输入

        try:
            msg[Date].append(message[-1])
        except:
            msg[Date] = [message[-1]]

        temp_list = []
        for i in message:
            temp_list.append(Message(role=i['role'], content=i['content']))

        summarize = ai_generation(self.ap, self.model)
        reply = await summarize.generate_reply(temp_list)

        msg_chain = MessageChain([
            # Quote(),
            At(ctx.event.sender_id),
            Plain(reply)
        ])
        await ctx.send_message("person", int(ctx.event.launcher_id), msg_chain)

        # 回复消息 ""
        print(self.model + "模型回复：" + reply)

        # ctx.add_return("reply", [reply])
        if reply != "AI生成超时":
            # 记录消息
            msg[Date].append({"role": "assistant", "content": reply})

            with open(f"{self.temp_folder}\\person_{str(ctx.event.sender_id)}_temp.json", 'w',
                      encoding="utf-8") as f:  # 保存记录
                json_str = json.dumps(msg, ensure_ascii=False)
                f.write(json_str)

#############################总结######################################
        if len(msg[Date]) > self.conversation_num + 2 or len(dates) > 1:

            summarize = Summarize(msg, self.model, self.user_name, self.assistant_name, int(ctx.event.launcher_id),
                                  self.summarize_lens, self.ap)
            await summarize.summarize_memory()

            ctx.prevent_default()  # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_postorder()

        else:
            ctx.prevent_default()  # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_postorder()


#######################################################################

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):

        Time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 获取时间
        Date = datetime.datetime.now().strftime('%Y-%m-%d')

        try:
            with open(f"{self.data_folder}\\group_{str(ctx.event.launcher_id)}_summarize.json", "r", encoding="utf-8") as f:
                summarize = json.load(f)
        except:
            summarize = {}

        try:
            with open(f"{self.temp_folder}\\group_{str(ctx.event.launcher_id)}_temp.json", "r", encoding="utf-8") as f:
                msg = json.load(f)

        except:
            msg = {Date: []}

        msg_user = ctx.event.text_message  # 这里的 event 即为 PersonNormalMessageReceived 的对象

        if msg_user == "查看总结":
            dates = summarize.keys()
            if len(dates) > 0:
                output = "当前总结：\n"
                for i in dates:
                    output += i + ":\n" + summarize[i] + "\n"
            else:
                output = "当前尚未生成总结"

            print("\n=== 以下为总结内容 ===")
            print(output)
            print("\n=== 以上为总结内容 ===")

            msg_chain = MessageChain([
                # Quote(),
                At(ctx.event.sender_id),
                Plain(output)
            ])
            await ctx.send_message("person", int(ctx.event.launcher_id), msg_chain)

            ctx.prevent_default()  # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_postorder()
            return

        message = []
        dates = list(msg.keys())
        temp_dates = copy.deepcopy(dates)

        while True:
            if len(temp_dates) > 1:
                for i in msg[temp_dates[0]]:
                    message.append(i)
                temp_dates.pop(0)
            else:
                for i in msg[temp_dates[0]]:
                    message.append(i)
                break

        message.insert(0, {"role": "system",
                           "content": f"{self.system_prompt}\n以下是先前对话的总结：{summarize}\n请根据以上信息作出符合{self.assistant_name}角色设定的回复，确保回复充分体现{self.assistant_name}的性格特征和情感反应。回复字数不超过{self.output_num}字。"})

        message.append({"role": "user", "content": '[' + Time + ']' + msg_user})  # 修饰输入

        try:
            msg[Date].append(message[-1])
        except:
            msg[Date] = [message[-1]]

        temp_list = []

        for i in message:
            temp_list.append(Message(role=i['role'], content=i['content']))

        summarize = ai_generation(self.ap, self.model)
        reply = await summarize.generate_reply(temp_list)

        msg_chain = MessageChain([
            # Quote(),
            At(ctx.event.sender_id),
            Plain(" " + reply)
        ])
        await ctx.send_message("group", int(ctx.event.launcher_id), msg_chain)

        # 回复消息 ""
        print(self.model + "模型回复：" + reply)

        if reply != "AI生成超时":
            # 记录消息
            msg[Date].append({"role": "assistant", "content": reply})

            with open(f"{self.temp_folder}\\group_{str(ctx.event.launcher_id)}_temp.json", 'w',
                      encoding="utf-8") as f:  # 保存记录
                json_str = json.dumps(msg, ensure_ascii=False)
                f.write(json_str)

        #############################总结######################################
        if len(msg[Date]) > self.conversation_num + 2 or len(dates) > 1:

            summarize = Summarize(msg, self.model, self.user_name, self.assistant_name, int(ctx.event.launcher_id),
                                  self.summarize_lens, self.ap)
            await summarize.summarize_memory()

            ctx.prevent_default()  # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_postorder()

        else:
            ctx.prevent_default()  # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_postorder()

    # 插件卸载时触发
    def __del__(self):
        pass
