import asyncio
import os
import sys
import logging
from pathlib import Path
from aiofile import async_open
from aiopath import AsyncPath
from aioshutil import copyfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def copy_file(file_path: AsyncPath, dest_path: AsyncPath):
    extension = file_path.suffix[1:].lower() if file_path.suffix else "no_extension"
    dest_folder = dest_path / extension
    await dest_folder.mkdir(parents=True, exist_ok=True)

    dest_file_path = dest_folder / file_path.name
    try:
        await copyfile(file_path, dest_file_path)
        logger.info(f"Copied {file_path} to {dest_file_path}")
    except Exception as e:
        logger.error(f"Error copying {file_path} to {dest_file_path}: {e}")


async def read_folder(src_path: AsyncPath, dest_path: AsyncPath):
    tasks = []
    async for item in src_path.iterdir():
        if await item.is_file():
            tasks.append(copy_file(item, dest_path))
        elif await item.is_dir():
            tasks.append(read_folder(item, dest_path))
    await asyncio.gather(*tasks)


async def main(src: str, dest: str):
    src_path = AsyncPath(src)
    dest_path = AsyncPath(dest)
    await read_folder(src_path, dest_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 task1.py <source_directory> [<destination_directory>]")
        sys.exit(1)

    src_directory = sys.argv[1]
    dest_directory = sys.argv[2] if len(sys.argv) >= 3 else "dest"

    asyncio.run(main(src_directory, dest_directory))
