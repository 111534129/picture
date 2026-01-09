@bp.app_template_filter('linkify_mentions')
def linkify_mentions(text):
    def replace(match):
        username = match.group(1)
        user = User.query.filter_by(username=username).first()
        if user:
            return f'<a href="{url_for("main.user", username=username)}">@{username}</a>'
        return match.group(0)
    return re.sub(r'@(\w+)', replace, text)
