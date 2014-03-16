<%inherit file="notaliens:core/templates/layout.mako"/>
<link href="${request.static_url('notaliens:static/chosen/chosen.min.css')}" rel="stylesheet">
<script type="text/javascript" src="${request.static_url('deform:static/scripts/deform.js')}"></script>
<script type="text/javascript" src="${request.static_url('notaliens:static/chosen/chosen.jquery.js')}"></script>
<h1>Profile</h1>
${form|n}

<%block name="javascript">
</%block>

