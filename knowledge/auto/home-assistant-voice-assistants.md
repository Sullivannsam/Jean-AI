# Research: Home Assistant voice assistants

> Auto-researched on 2026-09-02 17:50
> Fetched from source URLs below. Content is unedited extracts.

## Source: https://www.home-assistant.io/voice_control/

Assist - Talk to your smart home with Home Assistant - Home Assistant 

 2026.8.3

Getting started 

 Documentation

Installation 

Automations 

Dashboards 

Voice assistants 

Device organization 

Energy management 

Templating 

Configuration using the YAML file 

 Our hardware

Home Assistant Green 

Connect ZBT-2 

Connect ZWA-2 

Voice Preview Edition 

Integrations 

Blog 

Need help? 

 On this page Getting started 

Expand and experiment 

Supported languages and sentences 

Related topics 

Related links 

 Assist - Talk to your smart home with Home Assistant Assist is the voice assistant built into Home Assistant. It lets you control your smart home with natural language, and it can run fully on your own hardware, so your voice commands stay private. Assist works in the Home Assistant companion app, on dedicated voice hardware like the Home Assistant Voice Preview Edition, and on devices you build yourself with ESPHome. 

Look for the Assist icon at the top right of your dashboard to try it out right away. 

Assist is built on an open voice foundation and powered by knowledge contributed by our community. It can work locally or, if you prefer, use one of the latest large language models to handle more conversational requests. 

 Getting started 

When you configure voice assistant hardware made for Home Assistant, it will use a wizard to help you configure your system and get started to use voice. 

Our recommended voice assistant hardware is the Home Assistant Voice Preview Edition. 

In case your hardware does not support our wizard, do not worry. Here are two detailed guides based on how you plan to process your voice (Locally, or using Home Assistant Cloud voice services) 

I plan to process my voice locally 

I plan to use Home Assistant Cloud (recommended as it is the simplest) 

 Expand and experiment 

Once your setup is up and running and you follow the best practices, check all the possibilities we found for Expanding your Assist setup, and further experiment with different setups like wake words. Do you want to talk to Super Mario? Or another figure? If you want Assist to respond in a fun way, you can create an assistant with an AI personality. 

To further improve your setup, try building other voice assistant satellite devices that allow you to add Assist with wake words to all your rooms: 

Enable wake word detection on your Android phone to activate Assist hands-free by saying “Hey Jarvis” or “Hey Nabu”, even when your phone is locked. 

You can use ESPHome to create your own awesome voice assistant satellites based on inexpensive ESP32 microcontrollers, like @piitaya did with his 3D-printed R5 droid. Follow our tutorial to create your own for just $13. 

Another alternative voice satellite solution is the experimental Linux-Voice-Assistant project that uses the ESPHome protocol. It allows you to build a Linux-based voice assistant smart speaker that runs on any x64 or ARM64 hardware capable of handling local, on-device audio processing. This approach provides greater flexibility for customization. Because it runs on a full Linux system, it also gives you access to significantly more local computing resources for additional features and other integrations on the same satellite. On HAOS, you can run it using the Assist Satellite App if your Home Assistant machine has a connected microphone and speaker. 

If you are interested in a voice assistant that is not always listening, consider using Assist on an analog phone. It will only listen when you pick up the horn, and the responses are for your ears only. Follow our tutorial to create your own analog phone voice assistant. 

 Supported languages and sentences 

Assist aims to support more languages than other voice assistants, but this is still a work in progress, and we need your help. 

Check supported languages here 

 Choose your language 
 Afrikaans 
 Albanian 
 Amharic 
 Arabic 
 Armenian 
 Azerbaijani 
 Basque 
 Bengali 
 Bosnian 
 Bulgarian 
 Burmese 
 Cantonese 
 Catalan 
 Chinese (Cantonese) 
 Chinese (Mandarin) 
 Croatian 
 Czech 
 Danish 
 Dutch 
 English 
 Estonian 
 Filipino 
 Finnish 
 French 
 Galician 
 Georgian 
 German 
 Greek 
 Gujarati 
 Hebrew 
 Hindi 
 Hungarian 
 Icelandic 
 Indonesian 
 Irish 
 Italian 
 Japanese 
 Javanese 
 Kannada 
 Kazakh 
 Khmer 
 Korean 
 Lao 
 Latvian 
 Lithuanian 
 Luxembourgish 
 Macedonian 
 Malay 
 Malayalam 
 Maltese 
 Marathi 
 Mongolian 
 Nepali 
 Norwegian Bokmål 
 Pashto 
 Persian 
 Polish 
 Portuguese 
 Romanian 
 Russian 
 Serbian 
 Shanghainese 
 Sinhala 
 Slovak 
 Slovenian 
 Somali 
 Spanish 
 Sundanese 
 Swahili 
 Swahili 
 Swedish 
 Tamil 
 Telugu 
 Thai 
 Turkish 
 Ukrainian 
 Urdu 
 Uzbek 
 Vietnamese 
 Welsh 
 Zulu 

 Local 

Not supported 

Needs more work 

Usable 

Fully supported 

 Home Assistant Cloud 

Not supported 

Needs more work 

Usable 

Fully supported 

Assist already supports a wide range of languages. Use the built-in sentences to control entities and areas, or create your own sentences. 

Did Assist not understand your sentence? Contribute them. 

 Assist was introduced in Home Assistant 2023.2. 

 Related topics

 Assist on android

 Assist on apple

 Build a $13 voice remote using an esphome device

 Best practices with assist

 Related links

Home Assistant Cloud 

Voice Preview Edition 

 Help us improve our documentation 

 Suggest an edit to this page, or provide/view feedback for this page.

Edit 

Provide feedback 

View given feedback 

 ## Documentation Overview
 |
 FAQ
 |
 Glossary

 Automations

 Dashboards

 Voice assistants

 Assist up and running

Getting started - Local 

Getting started - Home Assistant Cloud 

 Best practices

Exposing entities to Assist 

Assigning areas to floors and an area to a device 

Aliases for entities, areas and floors 

Exposing scripts to LLMs 

Talking to Assist - Sentences starter pack 

 Expanding Assist

Creating a personality with AI 

Custom sentences 

Assist for Android 

Assist for Apple 

 Experiment with Assist setups

The Home Assistant Approach to Wake Words 

Wake words for Assist 

Tutorial: ESP32-S3-BOX voice assistant 

Tutorial: Customize the S3-BOX 

Tutorial: $13 voice assistant 

Tutorial: World's most private voice assistant 

Tutorial: Your daily summary by Assist 

Starting Assist from your dashboard 

Contribute to the Voice initiative 

 Troubleshooting

Troubleshooting Assist 

Troubleshooting the ESP32-S3-BOX 

Using Piper TTS in automations 

 Organization

 Home energy management

 Templating

 Common tasks

 Configuration

 Authentication

 Tools and helpers

 iOS and Android apps

 Official hardware

Home Assistant Green 

Home Assistant Connect ZBT-1 

Home Assistant Connect ZBT-2 

Home Assistant Connect ZWA-2 

Home Assistant Yellow 

Home Assistant Voice Preview Edition 

## On this page

Getting started 

Expand and experiment 

Supported languages and sentences 

Related topics 

Related links 

Back to top 

 Home Assistant is a project from the Open Home Foundation.

## Join us and contribute!

GitHub repo 

Developers Portal 

Design Portal 

Data Science Portal 

Community Forum 

Creator Network 

Works with Home Assistant 

Our community 

Reporting issues 

## System status

 Integration Alerts

Security Alerts 

 System Status

## Companion apps

iOS and Apple devices 

Android and Wear OS 

...and more! 

## Support us

Merch store 

Home Assistant Cloud 

## Governance

Privacy Notices 

Contributor License Agreement 

Terms of Service 

Code of Conduct 

Credits 

License 

## Follow us

Sign up for our newsletter 

 For partnership inquiries please check out Works with Home Assistant. For media, email our team. For other questions, you can contact support (No technical support!)

 This website uses privacy-first analytics to help us improve the site. You can view all data in our public dashboard.

 Website powered by Jekyll

 Originally based on the Oscailte theme

## Source: https://www.home-assistant.io/docs/configuration/

The configuration.yaml file - Home Assistant 

 2026.8.3

Getting started 

 Documentation

Installation 

Automations 

Dashboards 

Voice assistants 

Device organization 

Energy management 

Templating 

Configuration using the YAML file 

 Our hardware

Home Assistant Green 

Connect ZBT-2 

Connect ZWA-2 

Voice Preview Edition 

Integrations 

Blog 

Need help? 

 On this page Editing configuration.yaml

To set up file access and prepare an editor 

To find the configuration directory 

To edit the configuration file 

Validating the configuration 

Reloading the configuration to apply changes 

Troubleshooting the configuration 

Related topics 

 Home

 ▸ Documentation

 The configuration.yaml file

While you can configure most of Home Assistant from the user interface, a small number of integrations and power-user features still need a few lines in the configuration.yaml file. This page explains how that file works, so you can use it when you need to. 

Example of a configuration.yaml file, accessed using the File editor app on a Home Assistant Operating System installation.

 Editing configuration.yaml 

How you edit your configuration.yaml file depends on your editor preferences and the installation type you used to set up Home Assistant. Follow these steps: 

Set up file access and prepare an editor. 

Find the configuration directory. 

Edit the configuration.yaml file. 

Save your changes and reload the configuration to apply the changes. 

 To set up file access and prepare an editor 

Before you can edit a file, you need to know how to access files in Home Assistant and setup an editor.
File access depends on your installation type. If you use Home Assistant Operating System Home Assistant OS, the Home Assistant Operating System, is an embedded, minimalistic, operating system designed to run the Home Assistant ecosystem on single board computers (like the Raspberry Pi) or Virtual Machines. It includes Home Assistant Core, the Home Assistant Supervisor, and supports apps. Home Assistant Supervisor keeps it up to date, removing the need for you to manage an operating system. Home Assistant Operating System is the recommended installation type for most users. , you can use editor apps, for example. If you use Home Assistant Container Home Assistant Container is a standalone container-based installation of Home Assistant Core. Any OCI compatible runtime can be used, but the documentation focus is on Docker.[Learn more] , apps are not available. 

To set up file access on the Home Assistant Operating System, follow these steps: 

If you are unsure which option to choose, install the file editor app.

Alternatively, use the Studio Code Server app. This editor offers live syntax checking and auto-fill of various Home Assistant entities. But it looks more complex than the file editor. 

If you prefer to use a file editor on your computer, use the Samba app. 

 To find the configuration directory 

To look up the path to your configuration directory, go to Settings > System > Repairs. 

Select the three dots menu and select System information . 

Find out the location of the Configuration directory . 

Unless you changed the file structure, the default is as follows: -

 Home Assistant Operating System Home Assistant OS, the Home Assistant Operating System, is an embedded, minimalistic, operating system designed to run the Home Assistant ecosystem on single board computers (like the Raspberry Pi) or Virtual Machines. It includes Home Assistant Core, the Home Assistant Supervisor, and supports apps. Home Assistant Supervisor keeps it up to date, removing the need for you to manage an operating system. Home Assistant Operating System is the recommended installation type for most users. : the configuration.yaml is in the /config folder of the installation. 

 Home Assistant Container Home Assistant Container is a standalone container-based installation of Home Assistant Core. Any OCI compatible runtime can be used, but the documentation focus is on Docker.[Learn more] : the configuration.yaml is in the config folder that you mounted in your container. 

 To edit the configuration file 

Once you have located the config folder, you can edit your configuration.yaml file. How you edit the file depends on the editor you set up in step 1: 

 If you are using the File editor app : Open the app, navigate to the /config folder in the file browser on the left, and select the configuration.yaml file to open it in the editor. 

 If you are using the Studio Code Server app : Open the app, use the file explorer on the left to navigate to the configuration.yaml file, and select it to open in the editor. 

 If you are using Samba to access files : Navigate to the shared folder on your computer, locate the configuration.yaml file, and open it with your favorite text editor like Notepad++ or Visual Studio Code. 

 Note 

If you have watched any videos about setting up Home Assistant using configuration.yaml (particularly ones that are old), you might notice your default configuration file is much smaller than what the videos show. Don’t be concerned, you haven’t done anything wrong. Many items in the default configuration files shown in those old videos are now included in the default_config: line that you see in your configuration file. Refer to the default config integration for more information on what’s included in that line. 

 Validating the configuration 

After changing configuration or automation files, you can check if the configuration is valid. A configuration check is also applied automatically when you reload the configuration or when you restart Home Assistant. 

The method for running a configuration check depends on your installation type. Check the common tasks for your installation type: 

Configuration check on Operating System 

Configuration check on Container 

 Reloading the configuration to apply changes 

For configuration changes to become effective, the configuration must be reloaded. Most integrations in Home Assistant (that do not interact with devices A device is a model representing a physical or logical unit that contains entities. or services The term “service” in Home Assistant is used in the sense of an information
service . For example, the municipal waste management service that provides
entities for organic, paper, and packaging waste. In terms of functionality,
the information service is like a device. It is called service to avoid
confusion, as it does not come with a piece of hardware. ) can reload changes made to their configuration in configuration.yaml without needing to restart Home Assistant. 

Under Settings , select the three dots menu (top right) , select Restart Home Assistant > Quick reload . 

If you find that your changes were not applied, you need to restart. 

Select Restart Home Assistant . 

Note: This interrupts automations and scripts. 

 Troubleshooting the configuration 

If you run into trouble while configuring Home Assistant, refer to the configuration troubleshooting page. 

 Related topics

 Yaml syntax

 Creating and restoring backups

 Reloading the yaml configuration from tools

 Configuring file access on the operating system

 Troubleshooting the configuration

 Help us improve our documentation 

 Suggest an edit to this page, or provide/view feedback for this page.

Edit 

Provide feedback 

View given feedback 

 ## Documentation Overview
 |
 FAQ
 |
 Glossary

 Automations

 Dashboards

 Voice assistants

 Organization

 Home energy management

 Templating

 Common tasks

 Configuration

Home information 

People and user configuration 

Customizing entities 

Remote access to Home Assistant 

Securing your Home Assistant 

Storing secrets in YAML 

YAML syntax 

The configuration.yaml file 

Troubleshooting configuration 

Splitting up the configuration 

Packages 

Events 

State and state object 

Entities and domains 

Entity component platform options 

 Authentication

 Tools and helpers

 iOS and Android apps

 Official hardware

Home Assistant Green 

Home Assistant Connect ZBT-1 

Home Assistant Connect ZBT-2 

Home Assistant Connect ZWA-2 

Home Assistant Yellow 

Home Assistant Voice Preview Edition 

## On this page

Editing configuration.yaml

To set up file access and prepare an editor 

To find the configuration directory 

To edit the configuration file 

Validating the configuration 

Reloading the configuration to apply changes 

Troubleshooting the configuration 

Related topics 

Back to top 

 Home Assistant is a project from the Open Home Foundation.

## Join us and contribute!

GitHub repo 

Developers Portal 

Design Portal 

Data Science Portal 

Community Forum 

Creator Network 

Works with Home Assistant 

Our community 

Reporting issues 

## System status

 Integration Alerts

Security Alerts 

 System Status

## Companion apps

iOS and Apple devices 

Android and Wear OS 

...and more! 

## Support us

Merch store 

Home Assistant Cloud 

## Governance

Privacy Notices 

Contributor License Agreement 

Terms of Service 

Code of Conduct 

Credits 

License 

## Follow us

Sign up for our newsletter 

 For partnership inquiries please check out Works with Home Assistant. For media, email our team. For other questions, you can contact support (No technical support!)

 This website uses privacy-first analytics to help us improve the site. You can view all data in our public dashboard.

 Website powered by Jekyll

 Originally based on the Oscailte theme
