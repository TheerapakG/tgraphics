import tgraphics

tgraphics.init_with_backend('pygame')

window = tgraphics.Window.create()
label = tgraphics.text.Label("hello world", "'JetBrains Mono', Consolas, 'Courier New', monospace", False, False, 100)

window.target_element = label

tgraphics.run()

tgraphics.uninit()
