<%inherit file="notaliens:core/templates/layout.mako"/>
<ul>
% for user in users:
<li><a href="${request.route_url('people_profile', username=user.username)}">${user.profile.display_name}</a></li>
% endfor
</ul>
hi people
