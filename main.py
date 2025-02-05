# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.6
#   kernelspec:
#     display_name: base
#     language: python
#     name: python3
# ---

import re
import json
import sys
import requests
import os


def get_http_server_port(workspace_dir: str) -> int:
    """Extracts the HTTP server port from a log file in the specified workspace directory.


    In siyuan, the "path/to/workspace/temp/siyuan.log" file contains the HTTP server port number. This function reads the log file and extracts the port number.

    The extracted port number is returned as an integer. If no port is found, the function returns -1.

    Args:
        workspace_dir (str): The path to the workspace directory where the log file is located.

    Returns:
        int: The port number of the HTTP server if found, otherwise -1.

    Raises:
        FileNotFoundError: If the log file does not exist in the specified directory.
        IOError: If there is an issue reading the log file.

    Example:
        The log file contains the following line with the HTTP server port number:
        ```
        I 2025/01/26 17:37:08 serve.go:189: kernel [pid=31181] http server [127.0.0.1:56004] is booting
        ...
        I 2025/01/25 22:21:47 serve.go:189: kernel [pid=88564] http server [0.0.0.0:52916] is booting
        ```
        >>> workspace_dir = "/path/to/workspace"
        >>> port = get_http_server_port(workspace_dir)
        >>> print(port)
        52916
    """
    log_file = os.path.join(workspace_dir, "temp/siyuan.log")
    port = -1
    # print(log_file)
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "http server" in line:
                    match = re.findall(r'http server \[.*?:(\d+)\]', line)
                    if match:
                        port = match[-1]
        print(log_file, port, file=sys.stderr)
    except FileNotFoundError:
        port = -1
    return port


def fullTextSearchBlock(q:str, port:int):
    searchJson = {}
    searchJson["query"] = q
    searchJson["method"] = 0
    type = {}
    type["blockquote"] = True
    type["codeBlock"] = True
    type["document"] = True
    type["embedBlock"] = True
    type["heading"] = True
    type["htmlBlock"] = True
    type["list"] = True
    type["listItem"] = True
    type["mathBlock"] = True
    type["paragraph"] = True
    type["superBlock"] = True
    type["table"] = True
    searchJson["type"] = type
    searchJson["path"] = []
    searchJson["groupBy"] = 0
    searchJson["orderBy"] = 0
    
    try:
        data = json.dumps(searchJson)
        url = "http://127.0.0.1:"+ str(port)+"/api/search/fullTextSearchBlock"
        res = requests.post(url, data)
        print(port, data, res.text, file=sys.stderr)
        # res.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        return []
    resJson = json.loads(res.text)
    return resJson["data"]["blocks"]


# +
##### Test
# workspace_dir = "xxxxx/Siyuan"
# port = get_http_server_port(workspace_dir)
# blocks = fullTextSearchBlock("alfred", port=port)
# -

ICON_File = "./icon_file.png"
ICON_Block = "./icon_block.png"


# Note, block types in siyuan search results: 
# ```bash
#     NodeDocument
#     NodeParagraph
#     NodeHTMLBlock
#     NodeCodeBlock
#     NodeAttributeView
# ```
# We set the icon for `NodeDocument` to `ICON_File`, and others to `ICON_Block`.

def parseRes(resBlocks):
    itemList = []
    uid = 1
    for block in resBlocks:
        item = {}
        item["uid"] = uid
        item["title"] = block["content"].replace("<mark>", "").replace("</mark>", "")[:50]
        item["subtitle"] = block["workspace"] + ": " + block["hPath"]
        item["arg"] = "siyuan://blocks/" + block["id"]
        item["icon"] = {"path" : ICON_File if block['type'] == "NodeDocument" else ICON_Block}
        itemList.append(item)
        uid += 1
    items = {}
    items["items"] = itemList
    items_json = json.dumps(items)
    sys.stdout.write(items_json)


env = dict(os.environ)
workspace_dirs = [env[x] for x in env.keys() if x.startswith("SIYUAN_WORKSPACE_")]


# +
def main():
    alfredQuery = str(sys.argv[1])
    total_blocks = []
    for workspace_dir in workspace_dirs:
        port = get_http_server_port(workspace_dir)
        if port != -1:
            try:
                blocks = fullTextSearchBlock(alfredQuery, port=port)
                for block in blocks:
                    block["workspace"] = workspace_dir.split("/")[-1]
                total_blocks.extend(blocks)
            except Exception as e:
                print(e, file=sys.stderr)
    parseRes(total_blocks)

if __name__ == '__main__':
    main()

# +
# workspace_dirs = ["/Users/ay/SoftwareData/siyuan-noteplan",
#                   "/Users/ay/SoftwareData/siyuan-micc",
#                   "/Users/ay/SoftwareData/Siyuan"]
# total_blocks = []
# for workspace_dir in workspace_dirs:
#     port = get_http_server_port(workspace_dir)
#     if port != -1:
#         try:
#             blocks = fullTextSearchBlock("time", port=port)
#             total_blocks.extend(blocks)
#         except Exception as e:
#             print(e)
