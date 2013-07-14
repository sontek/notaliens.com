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
  <button type="submit" class="btn">Search</button>
</form>

<div class="sites">
    % for site in data['sites']:
    <div class="site">
        <div class="title">
            <a href="${request.route_url('sites_details', site_pk=site['pk'])}">${site['title']}</a>
            <p>${site['description']}</p>
        </div>
        <div class="screenshot"><img src="${request.static_url('notaliens:static/screenshots/site_%s.png' % site['pk'])}"/></div>
    </div>
    % endfor
</div>

<br class="clear" /.

<div class="pagination">
  <ul>
    % for i in range(0, data['pages']):
      <li ${'class=disabled' if data['current_page'] == i else ''}>
        <a href="${request.route_url('sites_index_paged', page=i)}" >${i+1}</a>
      </li>
    % endfor
  </ul>
</div>
