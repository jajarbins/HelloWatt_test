class Context:

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}










