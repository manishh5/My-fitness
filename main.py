import json
import os
from kivy.utils import platform
from calendar import month
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.filemanager import MDFileManager
from kivy.uix.image import Image
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDIconButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from plyer import filechooser
from kivy.uix.filechooser import FileChooserListView
from datetime import datetime
import calendar

months = [month for month in calendar.month_name if month]




class Main_App(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Purple"
        self.members = []  # List to store member information
        self.root = MDScreen()
        self.screens = [self.create_main_menu_screen()]
        self.root.add_widget(self.screens[0])
        self.load_members()
        return self.root
    
    def save_members(self):
        with open('members.json', 'w') as f:
            json.dump(self.members, f)

    
    def add_member(self, instance):
        member_info = {
            'name': self.name_field.text,
            'address': self.address_field.text,
            'phone': self.phone_field.text,
            'join_date': self.join_field.text,
            'fees_plan': self.fee_field.text,
            'occ': self.occ_field.text,
            'profile_picture': self.profile_image.source,
            'fees_pending': {month: False for month in months}
        }
        self.members.append(member_info)
        self.save_members()
        print("Member added!")
        
    def load_members(self):
        try:
            with open('members.json', 'r') as f:
                self.members = json.load(f)
        except FileNotFoundError:
            self.members = []
        for member in self.members:
            if 'fees_pending' not in member:
                member['fees_pending'] = {month: False for month in months}
            
        
    def on_stop(self):
        self.save_members()

    def create_main_menu_screen(self):
        screen = MDScreen()
        layout = BoxLayout(orientation='vertical')
        toolbar = MDTopAppBar(title="Dream Fitness Gym")
        layout.add_widget(toolbar)
        layout.add_widget(Widget(size_hint_y=None, height=150))
        logo = Image(source='logo.jpg', size_hint_y=None, height=600, width=500, allow_stretch=True)
        label = MDLabel(text="Welcome to Dream Fitness Gym", halign="center")
        button1 = MDRectangleFlatButton(text="View Members", pos_hint={'center_x': 0.5})
        button1.bind(on_press=self.on_button1_press)
        gap = Label(text="", size_hint_y=None, height=20)
        button2 = MDRectangleFlatButton(text="Add Members", pos_hint={'center_x': 0.5})
        button2.bind(on_press=self.on_button2_press)
        layout.add_widget(logo)
        layout.add_widget(label)
        layout.add_widget(button1)
        layout.add_widget(gap)
        layout.add_widget(button2)
        screen.add_widget(layout)
        return screen

    def on_button1_press(self, instance):
        screen = self.create_view_members_screen()
        self.screens.append(screen)
        self.root.clear_widgets()
        self.root.add_widget(screen)

    def create_view_members_screen(self):
        screen = MDScreen()
        layout = BoxLayout(orientation='vertical')
        toolbar = MDTopAppBar(title="View Members")
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back(x)]]
        layout.add_widget(toolbar)

        # Add a spacer to create space between the toolbar and the search bar
        spacer = Widget(size_hint_y=None, height=30)
        layout.add_widget(spacer)

        # Add a new BoxLayout to hold the search bar and filter buttons
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80)
        layout.add_widget(top_layout)

        # Add a new BoxLayout to hold the search bar
        search_bar_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        top_layout.add_widget(search_bar_layout)

        self.search_field = MDTextField(hint_text="  Search", size_hint_y=None, height=40)
        self.search_field.bind(on_text_validate=self.search_members)
        search_bar_layout.add_widget(self.search_field)

        # Add a new BoxLayout to hold the filter buttons
        self.filter_spinner = Spinner(
            text='Filter by',
            values=[
                'A-Z',
                'Z-A',
                'January',
                'February',
                'March',
                'April',
                'May',
                'June',
                'July',
                'August',
                'September',
                'October',
                'November',
                'December'
            ],
            size_hint=(None, None),
            size=(150, 40)
        )
        self.filter_spinner.bind(text=self.apply_filter)
        top_layout.add_widget(self.filter_spinner)


        
        # Add a new BoxLayout to hold the member list
        self.member_list = BoxLayout(orientation='vertical', spacing=10)
        layout.add_widget(self.member_list)
        
        
        self.update_member_list()

        screen.add_widget(layout)
        return screen
    
    def get_month_number(self, month_name):
        return months.index(month_name) + 1
    
    def apply_filter(self, instance, value):
        if value == 'A-Z':
            self.filter_members_az()
        elif value == 'Z-A':
            self.filter_members_za()
        elif value in months:
            month_number = self.get_month_number(value)
            self.update_member_list(month=month_number)
        else:
            self.update_member_list()


    def on_button2_press(self, instance):
        screen = self.create_add_members_screen()
        self.screens.append(screen)
        self.root.clear_widgets()
        self.root.add_widget(screen)

    def create_add_members_screen(self):
        screen = MDScreen()
        layout = BoxLayout(orientation='vertical')
        toolbar = MDTopAppBar(title="Add Members here")
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back(x)]]
        layout.add_widget(toolbar)
        self.profile_button = MDRectangleFlatButton(text="Select Profile Picture",pos_hint={'center_x': 0.5})
        self.profile_button.bind(on_press=self.select_profile_picture)
        gap = Label(text="", size_hint_y=None, height=20)
        self.profile_image = Image(source="", size_hint=(None, None), size=(1000, 300))
        layout.add_widget(self.profile_image)
        label = MDLabel(text="", halign="center")
        self.name_field = MDTextField(hint_text="  Name")
        self.address_field = MDTextField(hint_text="  Address")
        self.phone_field = MDTextField(hint_text="  Phone Number")
        self.join_field = MDTextField(hint_text="  dd mm yyyy")
        self.fee_field = MDTextField(hint_text="  Fees Plan")
        self.occ_field = MDTextField(hint_text="  Occupation")
        button = MDRectangleFlatButton(text="Tap to Add member", pos_hint={'center_x': 0.5})
        button.bind(on_press=self.add_member)
        
        layout.add_widget(label)
        layout.add_widget(gap)
        layout.add_widget(self.profile_button)
        layout.add_widget(self.name_field)
        layout.add_widget(self.address_field)
        layout.add_widget(self.phone_field)
        layout.add_widget(self.join_field)
        layout.add_widget(self.fee_field)
        layout.add_widget(self.occ_field)
        layout.add_widget(button)
        
        screen.add_widget(layout)
        return screen
    
    def filter_members_az(self):
        self.members.sort(key=lambda x: x['name'])
        self.update_member_list()

    def filter_members_za(self):
        self.members.sort(key=lambda x: x['name'], reverse=True)
        self.update_member_list()
        
    def filter_members_january(self, instance):
        self.update_member_list(month=1)

    def filter_members_february(self, instance):
        self.update_member_list(month=2)

    def filter_members_march(self, instance):
        self.update_member_list(month=3)

    def filter_members_april(self, instance):
        self.update_member_list(month=4)

    def filter_members_may(self, instance):
        self.update_member_list(month=5)

    def filter_members_june(self, instance):
        self.update_member_list(month=6)

    def filter_members_july(self, instance):
        self.update_member_list(month=7)

    def filter_members_august(self, instance):
        self.update_member_list(month=8)

    def filter_members_september(self, instance):
        self.update_member_list(month=9)

    def filter_members_october(self, instance):
        self.update_member_list(month=10)

    def filter_members_november(self, instance):
        self.update_member_list(month=11)

    def filter_members_december(self, instance):
        self.update_member_list(month=12)
        
        
    def update_member_list(self, month=None):
        self.member_list.clear_widgets()
        for member in self.members:
            if self.search_field.text.lower() in member['name'].lower():
                if month:
                    try:
                        join_date = datetime.strptime(member['join_date'], "%d %m %Y").strftime("%B")
                    except ValueError:
                        try:
                            join_date = datetime.strptime(member['join_date'], "%d %m %y").strftime("%B")
                        except ValueError:
                            continue
                    if join_date == datetime.now().strftime("%B") and month != datetime.now().month:
                        continue
                    if join_date == datetime.strftime(datetime.now().replace(month=month), "%B"):       
                        row_layout = BoxLayout(orientation='horizontal', spacing=10)
                        profile_image = Image(source=member['profile_picture'], size_hint_x=None, width=50, allow_stretch=False, keep_ratio=False)
                        profile_image.border = (30, 30, 30, 30)
                        row_layout.add_widget(profile_image)

                        info_layout = BoxLayout(orientation='horizontal')
                        name_and_fee_layout = BoxLayout(orientation='horizontal')
                        name_label = MDLabel(text=f"{member['name']}", halign="left", font_style="H5")
                        fee_label = MDLabel(text=f"{member['fees_plan']}", halign="left")
                        if self.is_fee_pending(member):
                            fee_label.text += " - Fee Pending"
                        name_and_fee_layout.add_widget(name_label)
                        name_and_fee_layout.add_widget(fee_label)
                        info_layout.add_widget(name_and_fee_layout)
                        row_layout.add_widget(info_layout)

                        self.member_list.add_widget(row_layout)
                        row_layout.bind(on_touch_down=lambda instance, touch, member=member, month=month: self.view_member_details(instance, touch, member, month))
                else:
                    row_layout = BoxLayout(orientation='horizontal', spacing=10)
                    profile_image = Image(source=member['profile_picture'], size_hint_x=None, width=50, allow_stretch=False, keep_ratio=False)
                    profile_image.border = (30, 30, 30, 30)
                    row_layout.add_widget(profile_image)

                    info_layout = BoxLayout(orientation='horizontal')
                    name_and_fee_layout = BoxLayout(orientation='horizontal')
                    name_label = MDLabel(text=f"{member['name']}", halign="left", font_style="H5")
                    fee_label = MDLabel(text=f"{member['fees_plan']}", halign="left")
                    if self.is_fee_pending(member):
                        fee_label.text += " - Fee Pending"
                    name_and_fee_layout.add_widget(name_label)
                    name_and_fee_layout.add_widget(fee_label)
                    info_layout.add_widget(name_and_fee_layout)
                    row_layout.add_widget(info_layout)

                    self.member_list.add_widget(row_layout)
                    row_layout.bind(on_touch_down=lambda instance, touch, member=member: self.view_member_details(instance, touch, member))
                    
    def calculate_last_paid_date(self, member):
        join_date = datetime.strptime(member['join_date'], "%d %m %Y")
        last_paid_date = join_date.replace(day=28) if join_date.month != 2 else join_date.replace(day=29)
        last_paid_date = last_paid_date.replace(year=last_paid_date.year if last_paid_date.month != datetime.now().month else datetime.now().year)
        return last_paid_date
    
    def is_fee_pending(self, member):
        last_paid_date = self.calculate_last_paid_date(member)
        days_since_last_paid = (datetime.now() - last_paid_date).days
        return days_since_last_paid >= 30
    
    
    def search_members(self, instance):
        self.update_member_list()
        
        
    # Define a method to handle the back button press
    def go_back(self, instance):
        if len(self.screens) > 1:
            self.root.clear_widgets()
            self.screens.pop()
            self.root.add_widget(self.screens[-1])

    # Define a method to get the previous screen
    def get_previous_screen(self):
        pass
    # You need to implement this method to get the previous screen
    # For example, you can store the previous screen in a variable
    # and return it here
        

    def select_profile_picture(self, instance):
        filechooser.open_file(on_selection=self.on_selection)

    def on_selection(self, selection):
        if selection:
            file_path = selection[0]
            self.profile_image.source = file_path
            self.exit_manager()


    def view_member_details(self, instance, touch, member, month=None):
        if instance.collide_point(*touch.pos):
            fee_pending = self.is_fee_pending(member)
            screen = self.create_member_details_screen(member=member, fee_pending=fee_pending, month=month)
            self.screens.append(screen)
            self.root.clear_widgets()
            self.root.add_widget(screen)
            
    def create_received_fee_button(self, member):
        received_button = MDRectangleFlatButton(text="Received Fee", on_release=lambda x: self.mark_fee_received(member))
        return received_button

    def mark_fee_received(self, member):
        current_month = datetime.now().strftime("%B")
        if 'fees_pending' in member and current_month in member['fees_pending']:
            if member['fees_pending'][current_month]:
                member['fees_pending'][current_month] = False
                self.save_members()
                self.update_member_list()
                self.go_back(None)
                self.hide_fee_pending_label(current_month)

    def create_member_details_screen(self, member, fee_pending, month=None):
        screen = MDScreen()
        layout = BoxLayout(orientation='vertical')
        toolbar = MDTopAppBar(title="Member Details")
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back(x)]]
        layout.add_widget(toolbar)
        
        details_layout = BoxLayout(orientation='horizontal', spacing=70)
    
        # Left side for image
        image_layout = BoxLayout(orientation='vertical', size_hint_x=0.5, padding='20dp')
        profile_image = Image(source=member['profile_picture'], size_hint=(1, 1), allow_stretch=True, keep_ratio=True, pos_hint={'top': 1})
        image_layout.add_widget(profile_image)
        
        # Delete button
        delete_button = MDRectangleFlatButton(text="Delete Member", on_release=lambda x: self.delete_member(member))
        image_layout.add_widget(delete_button)
        
        
        details_layout.add_widget(image_layout)

        # Right side for details
        details_box = BoxLayout(orientation='vertical', size_hint_x=0.7)
        details_box.add_widget(MDLabel(text=f"  Name: {member['name']}"))
        details_box.add_widget(MDLabel(text=f"  Address: {member['address']}"))
        details_box.add_widget(MDLabel(text=f"  Phone: {member['phone']}"))
        if month:
            details_box.add_widget(MDLabel(text=f"  Join Date: {month}"))
        else:
            details_box.add_widget(MDLabel(text=f"  Join Date: {member['join_date']}"))
        details_box.add_widget(MDLabel(text=f"  Fees Plan: {member['fees_plan']}"))
        details_box.add_widget(MDLabel(text=f"  Occupation: {member['occ']}"))
        
        # Add a new BoxLayout to hold the fee pending notification
        if fee_pending:
            fee_pending_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, padding='10dp')
            fee_pending_layout.add_widget(MDLabel(text="Fee Pending", theme_text_color='Custom', font_style='Button', bold=True))
            details_box.add_widget(fee_pending_layout)
        
        
        # Add the received button to the details box
        details_box.add_widget(self.create_received_fee_button(member))

        details_layout.add_widget(details_box)

        layout.add_widget(details_layout)
        screen.add_widget(layout)
        
        return screen
    
     
    
    def delete_member(self, member):
        # Remove the member from the list
        self.members.remove(member)
        
        # Save the updated list to the file
        self.save_members()
        
        # Go back to the previous screen
        self.go_back(None)
    
    
    def select_path(self, path):
        print("Selected path:", path)
        self.profile_image.source = path
        self.exit_manager()
        return path


    def exit_manager(self, *args):
        self.exit_manager.close()

    def add_member(self, instance):
        member_info = {
            'name': self.name_field.text,
            'address': self.address_field.text,
            'phone': self.phone_field.text,
            'join_date': self.join_field.text,
            'fees_plan': self.fee_field.text,
            'occ': self.occ_field.text,
            'profile_picture': self.profile_image.source
    }
        self.members.append(member_info)
        print("Member added!")
        
    

if __name__ == '__main__':
    Main_App().run()      