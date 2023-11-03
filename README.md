# How to preview the Atlas JSON file with a smooth look in Google Docs

Step 1. Replace Json data in the HTML-file using e.g. Sublime.
Everything below line 27 var jsonData = { down to }//

Step 2. Open the HTML file in your favorite browser

Step 3. Copy everything

Step 4. Paste it to Google Docs


# How to convert plain text from a Notion database into correctly formatted JSON and merge it with the Atlas file

## define notion settings

Before beginning, please ensure that Python and all required packages are installed.

1. Open the file called `.env`, or create it if it does not exist

If you have copied our Notion Databases available here, https://bluedelegate.notion.site/GAIT-work-automation-8cfde771e2e240eebfb0e03d3847e22e?pvs=4 , you can create the .env file using this simple guide: 
https://developers.notion.com/docs/create-a-notion-integration#getting-started

2. Fill in your details as such
```
NOTION_API_TOKEN = secret_xxxxxxxxxxxx
NOTION_API_BASE_URL = https://api.notion.com/v1
```

## run script to merge notion into atlas
have a local file called `atlas_converted.json` in the same folder as `maker_notion.py`. This is the atlas that we'll merge into. Then open a terminal in the same folder and write
```
python maker_notion.py
```
and it should create a file called `atlas_notion.json`. 