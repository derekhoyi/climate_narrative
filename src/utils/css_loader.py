from pathlib import Path
import requests

def _load_external_css():
	here = Path(__file__).resolve()
	for parent in [here.parent, *here.parents]:
		candidate = parent / 'assets' / 'style.css'
		if candidate.exists():
			try:
				return candidate.read_text(encoding='utf-8')
			except Exception:
				return ""
	return ""

def _load_bootstrap_css():
	url = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
	try:
		resp = requests.get(url, timeout=5)
		if resp.ok:
			return resp.text
	except Exception:
		return ""
	return ""
