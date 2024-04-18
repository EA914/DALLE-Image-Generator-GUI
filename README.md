# DALLE-3 Image Generator GUI with Dictation

* Web Based Version in https://github.com/EA914/DALLE-Image-Generator-GUI/tree/main/index

### Files:
* `dallecmd.py` --> command line tool that allows you to dictate a prompt and retrieve an image from that prompt
* `dallegui.py` --> GUI interface that allows you to either type a prompt or dictate a prompt to generate an image

### APIs Used:
* [OpenAI Image Generation](https://platform.openai.com/docs/guides/images?context=node)
* [OpenAI Speech-to-Text](https://platform.openai.com/docs/guides/speech-to-text)
* [Picovoice Porcupine](https://picovoice.ai/docs/porcupine/)
* [Picovoice Cobra](https://picovoice.ai/docs/cobra/)

## Screenshots / Demos

### `dallecmd.py`
![Dallecmd](https://i.imgur.com/X63TKqM.png)

Image generated (click for full-size: 

[<img src="https://i.imgur.com/5VIvDrO.png">](https://i.imgur.com/09yVMWo.png)

### `dalle.cmd.py` demo



https://github.com/EA914/DALLE-Image-Generator-GUI/assets/14112758/f1f07c9b-b505-42b9-ac91-fa203f1b3623



### `dallegui.py`
![dallegui](https://github.com/EA914/DALLE-Image-Generator-GUI/assets/14112758/3a449784-e076-43f8-aed8-90d0b513df4a)

### `dallegui.py` Generate Image demo



https://github.com/EA914/DALLE-Image-Generator-GUI/assets/14112758/3944acf9-7b79-4971-992d-acd7b1fb9e1a



### `dallegui.py` Dictate Image demo




https://github.com/EA914/DALLE-Image-Generator-GUI/assets/14112758/2a95e943-e268-4f12-af78-f479d656a458



## Additional Functionality
* Right click --> Save to save the image
* Click X to close the program

## Logging
Console contains logs of the payload that is sent and the JSON response from the API for debugging / logs.
![image](https://github.com/EA914/DALLE-Image-Generator-GUI/assets/14112758/5d2a2dd7-32e5-4f3d-b966-eda0af3fe430)

## .env File
* .env file should contain variable OPENAI_API_KEY which equals your OpenAI API key.
* .env file should contain variable PICOVOICE_API_KEY which equals your Picovoice API Key
