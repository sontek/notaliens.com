<%inherit file="notaliens:core/templates/layout.mako"/>
<div class="row">
  <div class="span2">
    % if request.user:
      % if request.user.pk == data['user'].pk:
        <div>
          <a href="${request.route_url('edit_profile', user_id=data['user'].pk)}"><button class="primary">Edit</button></a>
        </div>
      % endif
    % endif
    <img src="${data['user'].gravatar_url(size=120)}" />
  </div>
  <div class="span10">
      <div class="row">
        <div class="span8">
          <h2>${data['user'].profile.display_name}</h2>
          <h4>${data['user'].profile.location}</h4>
          <em>${data['user'].profile.one_liner}</em>
          % if data['user'].profile.description:
              <p>${data['user'].profile.description}</p>
          % endif

          <div class="skills">
            % for skill in data['user'].profile.skills:
              <span class="tag">${skill.name}</span>
            % endfor
          </div>
        </div>
        <div class="span2">
          <h4>People Near By</h4>
          % if 'near_by' in data:
            % for user in data['near_by']:
              <div>
                  <img src="${gravatar_url(user['email'], size=40)}" />
                  <a href="${request.route_url('people_profile', username=user['username'])}">${display_name(user)}</a>
                  <p>${display_location(user)}</p>
              </div>
            % endfor
          % endif
        </div>
      </div>
  </div>
</div>
