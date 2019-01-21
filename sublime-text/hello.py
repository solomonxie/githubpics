import sublime
import sublime_plugin


class ExampleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        #self.view.insert(edit, 0, "Hello, World!")
        clip = sublime.get_clipboard()
        self.view.insert(edit, 0, clip)

