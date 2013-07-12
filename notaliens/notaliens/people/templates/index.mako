<%inherit file="notaliens:core/templates/layout.mako"/>
<form class="form-search" method="POST">
      <div>
        <label>Search Text</label>
        % if 'search_text' in data:
          <input type="text" class="input-medium search-query" name="search" value="${data['search_text']}">
        % else:
          <input type="text" class="input-medium search-query" name="search">
        % endif
      </div>
      <div>
        <label>Postal Code</label>
        % if 'postal_code' in data:
          <input type="text" class="input-medium search-query" name="postal_code" value="${data['postal_code']}">
        % else:
          <input type="text" class="input-medium search-query" name="postal_code">
        % endif
        <label>Within</label>
        <select name="distance">
          % for i in [30, 60, 120]:
              % if 'distance' in data:
                  % if data['distance'] == i:  
                    <option selected="selected" value="${i}">${i}</option>
                  % else:
                    <option value="${i}">${i}</option>
                  % endif
              % else:
                  <option value="${i}">${i}</option>
              % endif
          % endfor
        </select>
      </div>
  <button type="submit" class="btn">Search</button>
</form>

<table class="table table-striped">
  <thead>
    <tr>
      <th>Name</th>
      <th>Username</th>
      <th>E-mail</th>
      <th>Location</th>
      <th>Available for work?</th>
      <th>Skills</th>
    </tr>
  </thead>
% for user in data['users']:
  <tr>
    <td>
      <a href="${request.route_url('people_profile', username=user['username'])}">${display_name(user)}</a>
    </td>
    <td>
      ${user['username']}
    </td>
    <td>
      ${user['email']}
    </td>
    <td>
      ${display_location(user)}
    </td>
    <td>
      % if user['profile']['available_for_work'] == False:
        No
      % else:
        Yes
      % endif
    </td>
    <td>
      ${', '.join([s['name'] for s in user['profile']['skills']])}
    </td>
  </tr>
% endfor
</table>
<div class="pagination">
  <ul>
    % for i in range(0, data['pages']):
      <li ${'class=disabled' if data['current_page'] == i else ''}>
        <a href="${request.route_url('people_index_paged', page=i)}" >${i+1}</a>
      </li>
    % endfor
  </ul>
</div>
