import os
import re

widget_dir = r"C:\Users\Loho Christopher\Desktop\Footprint_manager\frontend\src\features\dashboard\components\widgets"

for filename in os.listdir(widget_dir):
    if not filename.endswith(".tsx"):
        continue
    filepath = os.path.join(widget_dir, filename)
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # If it contains throw new Error, we replace it.
    if "throw new Error(" in content:
        # 1. Update destructuring to extract refetch
        if ", error }" in content:
            content = content.replace(", error }", ", error, refetch }")
        elif " error }" in content:
            content = content.replace(" error }", " error, refetch }")

        # 2. Extract title (usually the first string in the throw or from the title prop of WidgetCard)
        title_match = re.search(r'title="([^"]+)"', content)
        title = title_match.group(1) if title_match else "Widget"

        # We need to find the error message from the throw
        err_match = re.search(r"throw new Error\('([^']+)'\);", content)
        err_msg = err_match.group(1) if err_match else "Unable to load data"

        # 3. Replace the if (error) block
        new_block = f"""  if (error) {{
    return (
      <WidgetCard title="{title}" isLoading={{false}} isFetching={{false}}>
        <div style={{{{ padding: '1rem', textAlign: 'center', color: 'var(--color-danger, #ef4444)' }}}}>
          <p style={{{{ margin: '0 0 0.5rem 0', fontWeight: 500 }}}}>{err_msg}</p>
          <button
            onClick={{() => refetch()}}
            style={{{{
              background: 'transparent',
              border: '1px solid currentColor',
              color: 'inherit',
              padding: '0.25rem 0.75rem',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.75rem'
            }}}}
          >
            Retry
          </button>
        </div>
      </WidgetCard>
    );
  }}"""

        content = re.sub(r"  if \(error\) \{\s*throw new Error\('[^']+'\);\s*\}", new_block, content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

print("Widgets updated.")
