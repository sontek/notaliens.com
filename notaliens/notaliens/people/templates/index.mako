<%inherit file="notaliens:core/templates/layout.mako"/>
<ul>
% for user in users:
    <li>${user.profile.display_name}</li>
% endfor
</ul>
hi people
