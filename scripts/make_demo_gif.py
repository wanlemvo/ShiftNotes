"""Create a small animated overview from real captured UI stages."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "docs" / "demo"
STAGES = ("briefing", "dashboard", "trends", "comparison", "sources", "correction")


def main():
    frames = []
    for stage in STAGES:
        with Image.open(MEDIA / f"{stage}.png") as source:
            width = 1080
            frame = source.convert("RGB").resize(
                (width, round(source.height * width / source.width)),
                Image.Resampling.LANCZOS,
            )
            frames.append(frame.quantize(colors=128))
    frames[0].save(
        MEDIA / "overview.gif",
        save_all=True,
        append_images=frames[1:],
        duration=[2600] * len(frames),
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Created {MEDIA / 'overview.gif'} from {len(frames)} captured UI stages.")


if __name__ == "__main__":
    main()
