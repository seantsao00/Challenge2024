# Challenge2024
## CSIE Camp Challenge 2024 幻影的競技場

台大資訊系 2024 資訊營所使用的教學用遊戲原始碼。

## Document

- [遊戲簡介](https://hackmd.io/@shimeming/Challenge2024-public)

## Virtual Environment

推薦使用 virtual environment。以 bash/zsh 的 Linux 環境下，使用 [Venv](https://docs.python.org/3/library/venv.html) 為例：

- (Debian/Ubuntu) 確保安裝 `python3.11-venv`。可以用 `sudo apt install python3.11-venv` 安裝。
- 在根目錄運行 `python3 -m venv .venv`。
- 在根目錄運行 `source .venv/bin/activate`。
- 看到 prompt 前面出現 `(.venv)` 就成功啟動環境了。
- 運行 `pip install -r requirements.txt` 安裝 dependencies。

注意 `python3.11` 可能需要更新成其他更新的版本。

對於 VScode 使用者，可以直接使用內建指令創建虛擬環境。步驟如下：

- `Ctrl+Shift+P`，選取 Python: Create Environment...。
- 選取 Venv。
- 選取想要使用的 interpreter。一般來說，選取 `/bin/python3` 就好了。
- 在詢問要安裝的 dependencies 時，選擇 `requirements.txt`。

## For developers

### Commit Message Style

參考[這個](https://gist.github.com/ericavonb/3c79e5035567c8ef3267)。

### Format

請使用 [PEP 8](https://peps.python.org/pep-0008/) 統一格式。範例使用如下：

```sh
autopep8 --in-place --recursive .
```

這會在不改變行為的前提下修復大部分 PEP 8 問題。

VScode 使用者推薦使用這個 [extension](https://marketplace.visualstudio.com/items?itemName=ms-python.autopep8) 為預設 formatter。

另外，可選的使用 `isort`：

```sh
isort .
```

## Reminders

- 在 Windows 使用 `python`，在 MacOS/Linux 使用 `python3`。

## Challenge 2023

[Challenge 2023 repo](https://github.com/Ccucumber12/Challenge2023)

## Credit
### Game Design & Game Programming
- 王淇 littlecube8152
- 李瑞恩 LEbullient
- 周昀蓉 miachou1225
- 官毓韋 Achi-kyw
- 林映辰 MiriamLin
- 邱翊均 PixelCat31415
- 洪銘德 shimeming
- 胡祐誠 HyperSoWeak
- 高嘉泓 victor0206
- 常洧丞 WeberChange-dev
- 張閔堯 Yao1004
- 曹紹洵 seantsao00
- 笪瑜庭 iazzenma
- 陳愷欣 kxcathy
- 黃睿加 rueijiahuang
- 楊翔宇 racercode
- 蔡朝暐 JerryTsai12
- 鄭又齊 Dandan489
- 鄭詠堯 yungyaoc
- 蘇翊軒 brizxz

### Art
- 李佩恆 pei-heng-li
- 周昀蓉 miachou1225
- 邱子芹 cthziun
- 胡祐誠 HyperSoWeak
- 笪瑜庭 iazzenma
- 陳柏靜 ldOwObl
- 陳愷欣 kxcathy
- 陳嘉翎 ChiaLingChen
### Composition & Sound Design
- 黃睿加 rueijiahuang
### AI Design & Game Testing
- 王淇 littlecube8152
- 王褕立 FHVirus
- 高嘉泓 victor0206
- 劉丞浩 CppNoPointer
- 蔡朝暐 JerryTsai12
- 鄭詠堯 yungyaoc
- 蘇翊軒 brizxz
### Project Management & Quality Assurance
- 洪銘德 shimeming
- 曹紹洵 seantsao00
### Special Thanks
- 學術負責人　段蓉杉 tuanrongshan
- 主辦　資工系系學會
- 一起籌備資訊營的人們與參加資訊營的所有人

以上名字以中文筆畫數排序
