"""
StoneStory 终端命令测试

用法：
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


# 项目根目录。
PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TerminalCommandsTest(unittest.TestCase):
    """验证 StoneStory 终端命令包装脚本可正常工作。"""

    def test_stonestory_chat_help(self) -> None:
        """
        验证 stonestory-chat 脚本支持帮助输出。

        @params:
            无。

        @return:
            None。
        """
        result = subprocess.run(
            [str(PROJECT_ROOT / "scripts" / "stonestory-chat"), "--help"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        self.assertIn("StoneStory 对话上下文构造命令", result.stdout)
        self.assertIn("jia-baoyu", result.stdout)

    def test_baoyu_chat_generates_payload(self) -> None:
        """
        验证 baoyu-chat 脚本会调用现有 chat 构造流程并生成 payload。

        @params:
            无。

        @return:
            None。
        """
        result = subprocess.run(
            [str(PROJECT_ROOT / "scripts" / "baoyu-chat"), "你怎么看黛玉？"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, msg=result.stderr)
        self.assertIn("Character chat payload completed.", result.stdout)
        self.assertTrue((PROJECT_ROOT / "data" / "output" / "character_chat" / "jia-baoyu_prompt_payload.json").exists())

    def test_stonestory_eval_reports_missing_payload_for_invalid_flow(self) -> None:
        """
        验证评估脚本在缺少 payload 时会给出明确提示。

        @params:
            无。

        @return:
            None。
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            script_copy_dir = temp_root / "scripts"
            script_copy_dir.mkdir(parents=True)
            script_copy = script_copy_dir / "stonestory-eval"
            script_copy.write_text((PROJECT_ROOT / "scripts" / "stonestory-eval").read_text(encoding="utf-8"), encoding="utf-8")
            script_copy.chmod(0o755)

            result = subprocess.run(
                [str(script_copy), "jia-baoyu", "妹妹自然是极好的人。"],
                cwd=temp_root,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("Payload file not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
