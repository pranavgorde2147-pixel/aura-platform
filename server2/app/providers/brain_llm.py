from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.core.config import Config
from app.core.logging import build_logger

logger = build_logger(__name__)


@dataclass
class ModelLoadResult:
    ok: bool
    path: str
    message: str


class QwenBrainEngine:
    def __init__(self, config: Config):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._loaded = False
        self._load_model()

    def _load_model(self) -> None:
        model_dir = Path(self.config.MODEL_PATH)
        if not model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {model_dir}")

        start = time.time()
        logger.info("Loading Qwen3.5-4B from %s", model_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir), trust_remote_code=True, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            str(model_dir),
            torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )
        self.model.eval()
        self.model.to(self.device)
        self._loaded = True
        logger.info("Model loaded in %.2fs on %s", time.time() - start, self.device)

    def is_ready(self) -> bool:
        return self._loaded and self.model is not None and self.tokenizer is not None

    def generate(self, prompt: str, max_new_tokens: int = 256) -> str:
        if not self.is_ready():
            raise RuntimeError("Model is not loaded")

        messages = [{"role": "user", "content": prompt}]
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        )
        if self.device == "cuda":
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        else:
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return generated.strip()
