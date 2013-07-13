<%inherit file="notaliens:core/templates/layout.mako"/>
<form class="form" method="POST">
<label for="title">Title</label>
<input type="text" name="title" class="input-medium">
<label for="description">Description</label>
<input type="text" name="description" class="input-medium">
<label for="url">URL</label>
<input type="text" name="url" class="input-medium">
<button type="submit" class="btn">Submit Site</button>
</form>
