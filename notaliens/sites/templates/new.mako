<%inherit file="notaliens:core/templates/layout.mako"/>
<form class="form" method="POST">
<fieldset>
<legend>Site Details</legend>
<label for="title">Title</label>
<input type="text" name="title" class="input-medium">
<label for="description">Description</label>
<input type="text" name="description" class="input-medium">
<label for="url">URL</label>
<input type="text" name="url" class="input-medium">

<label for="python">Python Version</label>
<select name="python" multiple>
    <option value="python26">Python 2.6</option>
    <option value="python27">Python 2.7</option>
    <option value="python32">Python 3.2</option>
    <option value="python33">Python 3.3</option>
</select>

<label for="database">Data Storage</label>
<select name="database" multiple>
    <option value="redis">Redis</option>
    <option value="postgresql">PostgreSQL</option>
    <option value="mysql">MySQL</option>
    <option value="mongo">MongoDB</option>
</select>

<label for="oss">Open Source</label><input type="checkbox" name="oss">
<label for="oss-url">Source URL</label>
<input type="text" name="oss-url">
</fieldset>

<button type="submit" class="btn">Submit Site</button>
</form>
