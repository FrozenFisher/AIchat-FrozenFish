'''
借用qwen-agent的现成tools框架
如本pythonexecutor
给予python代码，tools将会输出类似('控制台输出', 'IndentationError: unexpected indent（是否报错）')('Hello world!', 'Done')
建立prompt自反馈，形成提问链，并改进qwen-agent的自反馈体系
只有用户按下回车后才能执行下一步，增加安全性

doc qa则可以作为prompt参考
'''