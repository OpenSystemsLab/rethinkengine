#  -*- coding: utf-8 -*-


class Signaling:
    __signals = {}

    def __init__(self):
        # nothing to do yet
        pass

    @classmethod
    def on_pre_save(cls, f):
        cls.__append_callback('pre_save', f)

    @classmethod
    def on_post_save(cls, f):
        cls.__append_callback('post_save', f)

    @classmethod
    def on_pre_update(cls, f):
        cls.__append_callback('pre_update', f)

    @classmethod
    def on_post_update(cls, f):
        cls.__append_callback('post_update', f)

    @classmethod
    def on_pre_delete(cls, f):
        cls.__append_callback('pre_delete', f)

    @classmethod
    def on_post_delete(cls, f):
        cls.__append_callback('post_delete', f)

    @classmethod
    def __append_callback(cls, e, f):
        model_name = cls.Meta.table_name
        if model_name not in cls.__signals:
            cls.__signals[model_name] = {}
        if e not in cls.__signals[model_name]:
            cls.__signals[model_name][e] = []
        cls.__signals[model_name][e].append(f)

    def _pre_save(self):
        self.__trigger_event('pre_save')

    def _post_save(self):
        self.__trigger_event('post_save')

    def _pre_update(self):
        self.__trigger_event('pre_update')

    def _post_update(self):
        self.__trigger_event('post_update')

    def _pre_delete(self):
        self.__trigger_event('pre_delete')

    def _post_delete(self):
        self.__trigger_event('post_delete')

    def __trigger_event(self, e):
        model_name = self.Meta.table_name
        if model_name not in self.__signals:
            return None

        if e in self.__signals[model_name]:
            for cb in self.__signals[model_name][e]:
                try:
                    cb(self)
                except Exception as e:
                    print e.message
