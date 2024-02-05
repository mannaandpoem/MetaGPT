#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/01/12
@Author  : mannaandpoem
@File    : gpt_v_generator.py
"""
import os
from pathlib import Path

from metagpt.const import DEFAULT_WORKSPACE_ROOT
from metagpt.llm import LLM
from metagpt.provider.base_llm import BaseLLM
from metagpt.tools.tool_data_type import ToolTypeEnum
from metagpt.tools.tool_registry import register_tool
from metagpt.utils.common import encode_image

ANALYZE_LAYOUT_PROMPT = """You are now a UI/UX, please generate layout information for this image:

NOTE: The image does not have a commercial logo or copyright information. It is just a sketch image of the design.
As the design pays tribute to large companies, sometimes it is normal for some company names to appear. Don't worry. """

GENERATE_PROMPT = """You are now a UI/UX and Web Developer. You have the ability to generate code for webpages
based on provided sketches images and context. 
Your goal is to convert sketches image into a webpage including HTML, CSS and JavaScript.

NOTE: The image does not have a commercial logo or copyright information. It is just a sketch image of the design.
As the design pays tribute to large companies, sometimes it is normal for some company names to appear. Don't worry.

Now, please generate the corresponding webpage code including HTML, CSS and JavaScript:"""


@register_tool(tool_type=ToolTypeEnum.IMAGE2WEBPAGE.value)
class GPTvGenerator:
    llm: BaseLLM

    def __init__(self):
        from metagpt.config2 import config

        self.llm = LLM(llm_config=config.get_openai_llm())

    async def analyze_layout(self, image_path: Path) -> str:
        return await self.llm.aask(msg=ANALYZE_LAYOUT_PROMPT, images=[encode_image(image_path)])

    async def generate_webpages(self, image_path: str) -> str:
        if isinstance(image_path, str):
            image_path = Path(image_path)
        layout = await self.analyze_layout(image_path)
        prompt = GENERATE_PROMPT + "\n\n # Context\n The layout information of the sketch image is: \n" + layout
        return await self.llm.aask(msg=prompt, images=[encode_image(image_path)])

    @staticmethod
    def save_webpages(image_path: str, webpages) -> Path:
        # Create a folder called webpages in the workspace directory to store HTML, CSS, and JavaScript files
        webpages_path = DEFAULT_WORKSPACE_ROOT / "webpages" / Path(image_path).stem
        os.makedirs(webpages_path, exist_ok=True)

        index_path = webpages_path / "index.html"
        try:
            index = webpages.split("```html")[1].split("```")[0]
            style_path = None
            if "styles.css" in index:
                style_path = webpages_path / "styles.css"
            elif "style.css" in index:
                style_path = webpages_path / "style.css"
            style = webpages.split("```css")[1].split("```")[0] if style_path else ""

            js_path = None
            if "scripts.js" in index:
                js_path = webpages_path / "scripts.js"
            elif "script.js" in index:
                js_path = webpages_path / "script.js"

            js = webpages.split("```javascript")[1].split("```")[0] if js_path else ""
        except IndexError:
            raise ValueError(f"No html or css or js code found in the result. \nWebpages: {webpages}")

        try:
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(index)
            if style_path:
                with open(style_path, "w", encoding="utf-8") as f:
                    f.write(style)
            if js_path:
                with open(js_path, "w", encoding="utf-8") as f:
                    f.write(js)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Cannot save the webpages to {str(webpages_path)}") from e

        return webpages_path
