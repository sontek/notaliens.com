<%inherit file="notaliens:core/templates/layout.mako"/>
<ul>
% for user in data['users']:
<li><a href="${request.route_url('people_profile', username=user['username'])}">${display_name(user)}</a></li>
% endfor
</ul>
hi people
