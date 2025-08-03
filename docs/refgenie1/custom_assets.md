# Use custom assets

Refgenie will write the genome configuration file automatically for any assets that you obtain using either `refgenie pull` or `refgenie build` -- but you can also take advantage of the refgenie system to manage your own custom assets in a few ways.

## Build a custom asset

The preferred option would be to script your asset building and then allow `refgenie` to manage it. In the next major version of `refgenie`, we intend to allow the `build` function to build arbitrary assets. So, all you would need to do is be able to provide a scripted recipe and you could use `refgenie` to build and manage those assets automatically. In the meantime, or if you have assets that you want managed but *can't* be scripted for some reason...

## Add custom assets

You can add additional assets with the `refgenie add` command. Just provide the genome, asset, and path *relative to the genome folder*. What this means is that you can exploit the refgenie system to manage and access your own assets. For example, say you have an hg38 annotation called *manual_annotation*, which you produced by hand. You can simply put that in your genomes folder (under `hg38/annotation_folder_dir`), and then add an entry to your genome configuration file:

```console
refgenie add hg38/manual_anno --path annotation_folder_dir --asset-class manual_anno
```

> Note: specified asset class needs to exist prior to adding the asset.

Now, you can access this asset with `refgenie` the same way you do all other assets... `refgenie list` will include it, `refgenie seek -g hg38 -a manual_anno` will retrieve the path, and from within python, `Refgenie.seek('hg38', 'manual_anno')` will also work. The advantage of doing this is that it lets you include *all* your genome-associated resources, including manual ones, within the same framework.
