# -*- coding: utf-8 -*-
import os
import re
import ast
import pickle
import vk_api
from vk_api import audio
import requests

from time import time
from datetime import datetime
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

from kivy import PY2
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import ConfigParser
from kivy.lang import Builder
from kivy.factory import Factory

if not PY2:
    Builder.load_string(open('ui.kv', encoding='utf-8').read())
else:
    Builder.load_file('ui.kv')
global my_id
global vk_audio
from bs4 import BeautifulSoup

class SortedListFood(Screen):
    def on_enter(self):

        # print('here\'s our storage:', App.get_running_app().user_data_dir)
        os.chdir(dirstart)
        USERDATA_FILE = r"AppData/UserData.datab"  # файл хранит логин, пароль и id

        if not (os.path.exists(USERDATA_FILE)):
            self.ids.rv.data.append({'viewclass': 'Label', 'text': "Внесите учетные данные в настройках"})
            self.ids.rv2.text = "Перейдите в настройки"
        else:
            self.ids.rv.data.append({'viewclass': 'Label', 'text': "Проверка данных прошла успешно"})
            self.ids.rv2.text = "Авторизоваться"
            self.ids.rv2.bind(on_release=self.getlogin)
            self.ids.rv2.bind(on_press=self.pi)

    def pi(self, *args):
        self.ids.rv.data.append({'viewclass': 'Label', 'text': "Работаем..."})

    def getlogin(self, *args):
        # import requests
        self.ids.rv2.unbind(on_release=self.getlogin)
        os.chdir(dirstart)
        USERDATA_FILE = r"AppData/UserData.datab"  # файл хранит логин, пароль и id
        global my_id
        with open(USERDATA_FILE, 'rb') as DataFile:
            LoadedData = pickle.load(DataFile)

        login = LoadedData[0]
        password = LoadedData[1]
        my_id = LoadedData[2]

        SaveData = [login, password, my_id]
        with open(USERDATA_FILE, 'wb') as dataFile:
            pickle.dump(SaveData, dataFile)

        vk_session = vk_api.VkApi(login=login, password=password)
        try:
            vk_session.auth()
        except:
            vk_session = vk_api.VkApi(login=login, password=password,
                                      auth_handler=auth_handler)
            vk_session.auth()

        vk = vk_session.get_api()
        from vk_api import audio
        global vk_audio

        vk_audio = vk_api.audio.VkAudio(vk_session)

        # get file and download
        config = ConfigParser()
        # config.read(os.path.join(dirstart, 'vkbona.ini'))
        config.read(os.path.join(os.path.dirname(__file__), 'vkbona.ini'))
        # path = config['General']['user_data']
        count = config['General']['default_count']

        self.ids.rv.data.append({'viewclass': 'Label', 'text': "Зашли на сервер"})
        self.ids.rv2.text = "Скачать " + count + " записей"
        self.ids.rv2.bind(on_release=self.getaudio)

    def getaudio(self, *args):
        self.ids.rv2.unbind(on_release=self.getaudio)
        print('Подготовка к скачиванию...')
        time_start = time()  # сохраняем время начала скачивания
        config = ConfigParser()
        config.read(os.path.join(dirstart, 'vkbona.ini'))
        config.read(os.path.join(os.path.dirname(__file__), 'vkbona.ini'))
        path = config['General']['user_data']
        countmax = int(config['General']['default_count'])
        os.chdir(path)  # меняем текущую директорию
        songs_list = list(vk_audio.get_iter(owner_id=my_id))
        print(len(songs_list))
        for i in songs_list:
            self.ids.rv.data.append({'viewclass': 'Label', 'text': i["artist"] + ' - ' + i["title"]})
        #songs_list=vk_audio.get_post_audio("-26797336", "78084")
        #soup = BeautifulSoup('https://vk.com/audios1593301', 'html.parser')
        #print(soup)
        #filter_root_el = {'id': 'search_owned_audios'}
        #root_el = soup.find(**filter_root_el)
        # if root_el is None:
        #    raise ValueError('Could not [441414141]')
        #else:print(root_el)
        #import requests
        #url = 'https://sports.betway.com/emoapi/emos'
        #data = '{"eventIds": [807789]}'
        #response = requests.post(url, data=data)
        #print(response.text)
        #kll=vk_api.audio.scrap_data('https://m.vk.com/audio', my_id, filter_root_el=None, convert_m3u8_links=True)
        print('kll')
        return

        self.ids.rv.data.append(
            {'viewclass': 'Label', 'text': 'Всего доступно: ' + str(len(songs_list)) + ' аудиозаписей.'})
        count = 0
        if countmax > 300:
            countmax = 300

        print("Скачивание началось...\n")
        # собственно циклом загружаем нашу музыку
        for i in songs_list[0:countmax]:

            if count > countmax:
                self.ids.rv.data.append({'viewclass': 'Label', 'text': 'лимит записей превышен: '})
                break
            if not (os.path.exists(os.path.abspath(os.curdir) + '/' + i["artist"] + ' - ' + i["title"] + '.mp3')):

                try:
                    print('Скачивается: ' + i["artist"] + " - " + i[
                    "title"])  # выводим информацию о скачиваемой в данный момент аудиозаписи

                    audio = songs_list[count]
                    print(audio)
                    url = audio["url"]
                    #print(string)
                    #newstring = re.split(r'/', string)
                    #print(newstring)

                    #url = '{}//{}/{}/{}'.format(newstring[0], newstring[2], newstring[3], newstring[4])
                    #print(url)

                    r = requests.get(url)
                    count += 1
                    if r.status_code == 200:
                        self.ids.rv.data.append(
                            {'viewclass': 'Label', 'text': 'Скачивание завершено: ' + i["artist"] + " - " + i["title"]})
                        with open(i["artist"] + ' - ' + i["title"] + '.mp3', 'wb') as output_file:
                            output_file.write(r.content)
                except OSError:
                    self.ids.rv.data.append(
                        {'viewclass': 'Label', 'text': "!!! Не удалось скачать аудиозапись №" + count})
            else:
                self.ids.rv.data.append(
                    {'viewclass': 'Label', 'text': 'Cкачано ранее: ' + i["artist"] + " - " + i["title"]})
        time_finish = time()

        self.ids.rv.data.append(
            {'viewclass': 'Label', 'text': 'На работу затрачено ' + str(int(time_finish - time_start)) + ' сек'})
        self.ids.rv2.text = "Авторизоваться"
        self.ids.rv2.bind(on_release=self.getlogin)


class AddFood(Screen):
    _app = ObjectProperty()

    def auth_handler(self, remember_device=None):
        code = input("Введите код подтверждения\n> ")
        if (remember_device == None):
            remember_device = True
        return code, remember_device

    def SaveUserData(self, login, password, profile_id):
        USERDATA_FILE = r"AppData/UserData.datab"
        SaveData = [login, password, profile_id]

        with open(USERDATA_FILE, 'wb') as dataFile:
            pickle.dump(SaveData, dataFile)

    def button_clicked(self, input_food, input_food2, input_food3):
        os.chdir(dirstart)
        USERDATA_FILE = r"AppData/UserData.datab"  # файл хранит логин, пароль и id
        global my_id

        if (os.path.exists(USERDATA_FILE)):
            os.remove(USERDATA_FILE)

        login = input_food
        password = input_food2
        my_id = input_food3
        self.SaveUserData(login, password, my_id)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Setting(Screen):
    _app = ObjectProperty()
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def on_enter(self):
        config = ConfigParser()
        # config.read(os.path.join(dirstart, 'vkbona.ini'))
        config.read(os.path.join(os.path.dirname(__file__), 'vkbona.ini'))
        self.field_path.text = config['General']['user_data']
        self.field_count.text = config['General']['default_count']

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        content.ids['filechooser'].path =r"/"
        self._popup = Popup(title="Выберете папку", content=content,
                            size_hint=(0.8, 0.7))
        self._popup.open()

    def save(self, path, filename):
        # with open(os.path.join(path, filename), 'w') as stream:
        # pass
        # stream.write(self.text_input.text)
        filename2 = os.path.join(path, filename)
        # print(type(filename2))
        newstring = filename2.split('/')  # \//
        # print(newstring)
        index = newstring[-1].find(".")
        # print(range(len(newstring)-2))
        if index != -1:
            filename2 = ""
            for i in range(len(newstring) - 1):
                filename2 += newstring[i]
                if newstring[i] != newstring[-2]:
                    filename2 += "/"
        # print(filename2)
        self.field_path.text = filename2
        self.dismiss_popup()

    def save_ini(self):
        config = ConfigParser()
        # config.read(os.path.join(dirstart, 'vkbona.ini'))
        config.read(os.path.join(os.path.dirname(__file__), 'vkbona.ini'))
        config['General']['user_data'] = self.field_path.text  # update
        config['General']['default_count'] = self.field_count.text  # create
        config.write()


class VkBonaApp(App):

    def on_pause(self):
        # Here you can save data if needed
        return True

    def on_resume(self):
        # Here you can check if any data needs replacing (usually nothing)
        pass

    def __init__(self, **kvargs):
        super(VkBonaApp, self).__init__(**kvargs)

        self.config = ConfigParser()
        self.screen_manager = Factory.ManagerScreens()
        self.user_data = {}

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'user_data', '/AppData')
        config.setdefault('General', 'default_count', '50')

        vk_file = "vk_config.v2.json"
        # REQUEST_STATUS_CODE = 200

        # global path
        # path = 'vk_music/'
        global dirstart
        dirstart = os.getcwd()

        # make folder in dir
        if (not os.path.exists("AppData")):
            os.mkdir("AppData")
        # if not os.path.exists(path):
        # os.makedirs(path)

    def set_value_from_config(self):
        self.config.read(os.path.join(self.directory, '%(appname)s.ini'))
        self.user_data = ast.literal_eval(self.config.get(
            'General', 'user_data'))

    def get_application_config(self):
        return super(VkBonaApp, self).get_application_config(
            '{}/%(appname)s.ini'.format(self.directory))

    def build(self):
        return self.screen_manager


if __name__ == '__main__':
    VkBonaApp().run()