from dash import dash_table
from html import escape as _html_escape
from markdown import markdown as _md
import os
import base64
import mimetypes
from pathlib import Path
SERIALIZATION_CACHE = {}


def filter_yml_by_scenario(yml, scenario, scenario_mapping_df):
	filtered_scenario_mapping_df = scenario_mapping_df[scenario_mapping_df['scenario_name'] == scenario]
	scenario_risk_type = filtered_scenario_mapping_df['risk_type'].iloc[0]
	scenario_risk_level = filtered_scenario_mapping_df['risk_level'].iloc[0]
	return yml[scenario_risk_type][scenario_risk_level]

def filter_user_selection_by_section(user_selection_df, section, sub_section):
	filtered_user_selection_df = user_selection_df[
		(user_selection_df['output_structure'] == section)
		& (user_selection_df['sub_section'] == sub_section)
	]
	return filtered_user_selection_df

def convert_to_bullet_points(df, bullet_point_column_name):
	groupby_variables_list = [x for x in df if x != bullet_point_column_name]
	output_df = df.sort_values(bullet_point_column_name)
	output_df[bullet_point_column_name] = output_df[bullet_point_column_name].astype(str)
	output_df = output_df.groupby(
		groupby_variables_list, as_index=False).agg({bullet_point_column_name: '\n- '.join})
	output_df[bullet_point_column_name] = '- ' + output_df[bullet_point_column_name]
	return output_df

def load_external_css():
	here = Path(__file__).resolve()
	for parent in [here.parent, *here.parents]:
		candidate = parent / 'assets' / 'css' / 'style.css'
		if candidate.exists():
			try:
				return candidate.read_text(encoding='utf-8')
			except Exception:
				return ""
	return ""

def _style_dict_to_css(style):
	if not style:
		return ''
	return '; '.join(f'{str(k).replace("_", "-")}:{v}' for k, v in style.items())

def _inline_image_src(src):
	src = 'src/' + src
	if not src:
		return ''
	if src.startswith(('http://', 'https://', 'data:')):
		return src
	if os.path.exists(src):
		mime, _ = mimetypes.guess_type(src)
		if not mime:
			mime = 'application/octet-stream'
		with open(src, 'rb') as f:
			b64 = base64.b64encode(f.read()).decode('utf-8')
		return f'data:{mime};base64,{b64}'
	return src

def _serialize_datatable(dt):
	cols = getattr(dt, 'columns', []) or []
	data = getattr(dt, 'data', []) or []
	col_ids = [c.get('id') for c in cols]
	header_html = '<tr>' + ''.join(
		f'<th>{_html_escape(str(c.get("name", c.get("id", ""))))}</th>' for c in cols
	) + '</tr>'
	body_rows = []
	for row in data:
		body_rows.append(
			'<tr>' + ''.join(
				f'<td>{_html_escape("" if row.get(cid) is None else str(row.get(cid)))}</td>'
				for cid in col_ids
			) + '</tr>'
		)
	return f'<table class="datatable"><thead>{header_html}</thead><tbody>{"".join(body_rows)}</tbody></table>'

def _markdown_to_html(text):
	if text is None:
		return ''
	if not _md:
		return f'<p>{_html_escape(str(text))}</p>'
	import re
	html = _md(str(text))

	# Inline <img> tags (produced by markdown from ![]()) and local paths -> data URIs
	def _inline_img(match):
		pre_attrs, src, post_attrs = match.group(1), match.group(2), match.group(3)
		# Preserve existing alt if present
		alt_match = re.search(r'alt="([^"]*)"', pre_attrs + post_attrs)
		alt = alt_match.group(1) if alt_match else ''
		inlined_src = _html_escape(_inline_image_src(src))
		return f'<img src="{inlined_src}" alt="{_html_escape(alt)}" />'
	html = re.sub(r'<img\s+([^>]*?)src="([^"]+)"([^>]*)>', _inline_img, html, flags=re.IGNORECASE)

	# Normalize links: ensure target + rel, keep inner HTML (do not escape inner)
	def _inline_link(match):
		pre_attrs, href, post_attrs, inner = match.group(1), match.group(2), match.group(3), match.group(4)
		escaped_href = _html_escape(href)
		return f'<a href="{escaped_href}" target="_blank" rel="noopener noreferrer">{inner}</a>'
	html = re.sub(r'<a\s+([^>]*?)href="([^"]+)"([^>]*)>(.*?)</a>', _inline_link, html, flags=re.IGNORECASE | re.DOTALL)

	return html

def serialize_component(component):
	if component is None:
		return ''
	# Primitive
	if isinstance(component, (str, int, float)):
		return _html_escape(str(component)).replace('\n', ' ')
	# List / tuple
	if isinstance(component, (list, tuple)):
		return ''.join(serialize_component(c) for c in component)
	# Avoid re-serializing same object (by id())
	cid = id(component)
	if cid in SERIALIZATION_CACHE:
		return SERIALIZATION_CACHE[cid]

	# DataTable
	if isinstance(component, dash_table.DataTable):
		html_str = _serialize_datatable(component)
		SERIALIZATION_CACHE[cid] = html_str
		return html_str

	cls_name = component.__class__.__name__

	# dcc.Markdown
	if cls_name == 'Markdown':
		html_str = _markdown_to_html(getattr(component, 'children', '')[0])
		SERIALIZATION_CACHE[cid] = html_str
		return html_str

	# Map Dash HTML component class names to tag
	tag = cls_name.lower()

	children = getattr(component, 'children', None)
	inner_html = ''
	if isinstance(children, (list, tuple)):
		inner_html = ''.join(serialize_component(c) for c in children)
	else:
		inner_html = serialize_component(children)

	attrs = []
	comp_id = getattr(component, 'id', None)
	if comp_id:
		attrs.append(f'id="{_html_escape(str(comp_id))}"')
	class_name = getattr(component, 'className', None)
	if class_name:
		attrs.append(f'class="{_html_escape(str(class_name))}"')
	style = getattr(component, 'style', None)
	style_css = _style_dict_to_css(style)
	if style_css:
		attrs.append(f'style="{_html_escape(style_css)}"')

	# Anchor specific
	if tag == 'a':
		href = getattr(component, 'href', None)
		if href:
			attrs.append(f'href="{_html_escape(str(href))}"')
		target = getattr(component, 'target', None)
		if target:
			attrs.append(f'target="{_html_escape(str(target))}"')

	# Image specific
	if tag == 'img':
		src = getattr(component, 'src', None)
		if src:
			attrs.append(f'src="{_html_escape(_inline_image_src(src))}"')
		alt = getattr(component, 'alt', '') or ''
		attrs.append(f'alt="{_html_escape(str(alt))}"')

	void_tags = {'img', 'br', 'hr', 'meta', 'link', 'input'}
	attr_str = (' ' + ' '.join(attrs)) if attrs else ''
	if tag in void_tags:
		html_str = f'<{tag}{attr_str} />'
		SERIALIZATION_CACHE[cid] = html_str
		return html_str

	html_str = f'<{tag}{attr_str}>{inner_html}</{tag}>'
	SERIALIZATION_CACHE[cid] = html_str
	return html_str

def wrap_full_html(body_html: str) -> str:
	return (
		'<!DOCTYPE html><html><head><meta charset="utf-8">'
		'<title>Report</title>'
		f'<style>{load_external_css() or ""}</style>'
		'</head><body>'
		f'{body_html}'
		'</body></html>'
	)
