# Message_Recorder

<!--
## 插件开发者详阅

### 开始

此仓库是 LangBot 插件模板，您可以直接在 GitHub 仓库中点击右上角的 "Use this template" 以创建你的插件。  
接下来按照以下步骤修改模板代码：

#### 修改模板代码

- 修改此文档顶部插件名称信息
- 将此文档下方的`<插件发布仓库地址>`改为你的插件在 GitHub· 上的地址
- 补充下方的`使用`章节内容
- 修改`main.py`中的`@register`中的插件 名称、描述、版本、作者 等信息
- 修改`main.py`中的`MyPlugin`类名为你的插件类名
- 将插件所需依赖库写到`requirements.txt`中
- 根据[插件开发教程](https://docs.langbot.app/plugin/dev/tutor.html)编写插件代码
- 删除 README.md 中的注释内容


#### 发布插件

推荐将插件上传到 GitHub 代码仓库，以便用户通过下方方式安装。   
欢迎[提issue](https://github.com/RockChinQ/LangBot/issues/new?assignees=&labels=%E7%8B%AC%E7%AB%8B%E6%8F%92%E4%BB%B6&projects=&template=submit-plugin.yml&title=%5BPlugin%5D%3A+%E8%AF%B7%E6%B1%82%E7%99%BB%E8%AE%B0%E6%96%B0%E6%8F%92%E4%BB%B6)，将您的插件提交到[插件列表](https://github.com/stars/RockChinQ/lists/qchatgpt-%E6%8F%92%E4%BB%B6)

下方是给用户看的内容，按需修改
-->
## 插件开发者详阅
配置完成 [LangBot](https://github.com/RockChinQ/LangBot) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get https://github.com/wakin721/Message_Recorder
```

由于项目仍然处于开发中，建议随时更新插件以获得更好的体验：

```
!plugin update https://github.com/wakin721/Message_Recorder
```

查看详细的[插件安装说明](https://docs.langbot.app/plugin/plugin-intro.html#%E6%8F%92%E4%BB%B6%E7%94%A8%E6%B3%95)

## 注意事项

插件仍然处于开发过程中，可能会出现各种情况，包括但不限于token消失术，当前回忆总结机制尚未完善，请谨慎使用。

## 使用
1.启动插件后会自动在data/plugins/Message_Recorder生成回忆文件夹和临时文件夹；自动从data/scenario/default.json读取提示词文件并生成配置文件，在card文件夹生成card.json。

2.配置文件card.json由system_prompt（系统提示）、user_name（对话者在角色扮演中的角色）、assistant_name（ai所扮演的角色）、summarize_lens（生成回忆的长度）、conversation_num（临时对话的数量）、output_num（输出字数，在提示词中限制，可能没有作用）、summary_date（调用回忆的天数，若要调用全部回忆，该参数为0）构成，系统自动总结生成的user_name和assistant_name可能不准确，请自行核验。

3.目前插件仍在开发中，遇到任何问题欢迎反馈。
<!-- 插件开发者自行填写插件使用说明 -->



## 版本
preview1.4：更新回忆调用机制，可设置调用回忆的天数。

preview1.3：修复了一点bug。

preview1.2：更新了聊天记录的保存及回忆生成逻辑，可以通过输入命令：查看回忆 查看已生成的回忆。

preview1.1：优化代码，增加模型生成的超时机制。

preview1.0：随便写了一个记忆插件，代码参考了小馄饨的QQSillyTavern：https://github.com/sanxianxiaohuntun/QQSillyTavern

<!-- 插件开发者自行填写插件使用说明 -->
