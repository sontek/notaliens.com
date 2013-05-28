<%inherit file="notaliens:core/templates/layout.mako"/>
<a href="${request.route_url('people_index')}">Back to list</a>

<div class="row">
  <div class="span3">
    % if request.user:
      % if request.user.pk == user.pk:
        <div>
          <a href="${request.route_url('edit_profile', user_id=user.pk)}"><button class="primary">Edit</button></a>
        </div>
      % endif
    % endif
    <img src="${user.gravatar_url(size=120)}" />
    <h3>${user.profile.display_name}</h3>
    <em>${user.profile.one_liner}</em>
  </div>
  <div class="span9">
    % if user.profile.description:
      <h3>About</h3>
      <div>
          ${user.profile.description}
      </div>
    % endif
  </div>
</div>
