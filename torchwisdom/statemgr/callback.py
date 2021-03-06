from typing import *
from torchwisdom.statemgr.state import *
from torchwisdom.statemgr.manager import *
from torchwisdom.callback import Callback
import time
from torchwisdom.core import *


class StateManagerCallback(Callback):
    def __init__(self):
        super(StateManagerCallback, self).__init__()
        self.statemgr: StateManager = None

    def on_fit_begin(self, *args: Any, **kwargs: Any) -> None:
        epoch_num = kwargs.get('epoch_num')
        trainer_state: TrainerState = self.statemgr.get_state('trainer')
        epoch_state: Dict = trainer_state.get_property('epoch')
        epoch_state['start'] = 0
        epoch_state['curr'] = 0
        epoch_state['num'] = epoch_num

        dcoll_state: DataCollectorState = self.statemgr.get_state('datacoll')
        dcoll_state.set_property('batch_size', self.trainer.data.batch_size)
        dcoll_state.set_property('num_workers', self.trainer.data.num_workers)
        dcoll_state.set_property('shuffle', self.trainer.data.shuffle)
        dcoll_state.get_property('train')['len'] = self.trainer.data.trainset.__len__()
        dcoll_state.get_property('valid')['len'] = self.trainer.data.validset.__len__()

    def on_fit_end(self, *args: Any, **kwargs: Any) -> None:
        pass

    def on_epoch_begin(self, *args: Any, **kwargs: Any) -> None:
        epoch_state: Dict = self.statemgr.get_state('trainer').get_property('epoch')
        epoch_state['time_start'] = time.time()

    def on_epoch_end(self, *args: Any, **kwargs: Any) -> None:
        # print("StateManagerCallback: on_epoch_end")
        statemgr: StateManager = self.statemgr
        trainer_state: TrainerState = self.statemgr.get_state('trainer')
        epoch_state: Dict = trainer_state.get_property('epoch')

        start = epoch_state.get('time_start')
        end = time.time()
        delta_time = end - start
        epoch_state['time_end'] = end
        epoch_state['time'].append(delta_time)

        epoch_num = epoch_state['num']
        elapsed_time = sum(epoch_state['time'])
        tremain = (delta_time * epoch_num) - elapsed_time
        if tremain <= 0: tremain = 0
        epoch_state['remain'].append(tremain)
        epoch_state['curr'] += 1
        statemgr.save()


class ModelCheckPointCallback(Callback):
    def __init__(self):
        super(ModelCheckPointCallback, self).__init__()
        self.statemgr: StateManager = None

    def on_fit_begin(self, *args: Any, **kwargs: Any) -> None:
        pass

    def on_fit_end(self, *args: Any, **kwargs: Any) -> None:
        pass

    def on_epoch_end(self, *args: Any, **kwargs: Any) -> None:
        pass