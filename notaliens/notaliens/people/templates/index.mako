<%inherit file="notaliens:core/templates/layout.mako"/>
<form class="form-search pull-right" method="POST">
  % if 'search_text' in data:
      <input type="text" class="input-medium search-query" name="search" value="${data['search_text']}">
  % else:
      <input type="text" class="input-medium search-query" name="search">
  % endif
  <button type="submit" class="btn">Search</button>
</form>

<table class="table table-striped">
  <thead>
    <tr>
      <th>Name</th>
      <th>E-mail</th>
      <th>Location</th>
    </tr>
  </thead>
% for user in data['users']:
  <tr>
    <td>
      <a href="${request.route_url('people_profile', username=user['username'])}">${display_name(user)}</a>
    </td>
    <td>
      ${user['email']}
    </td>
    <td>
      N/A
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
