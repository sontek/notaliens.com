<%inherit file="notaliens:core/templates/layout.mako"/>

<div class="title">
    <a href="">${site.title}</a>
    <p>${site.description}</p>
</div>
<div class="screenshot"><img src="${request.static_url('notaliens:static/screenshots/site_%s.thumbnail.png' % site.pk)}"/></div>
