class Node:
    def prep(self, input_ctx):
        return input_ctx
    
    def exec(self, prep_output):
        return prep_output
    
    def post(self, input_ctx, exec_output):
        return exec_output
    
    def run(self, input_ctx):
        prep_output = self.prep(input_ctx)
        exec_output = self.exec(prep_output)
        post_output = self.post(input_ctx, exec_output)
        return post_output