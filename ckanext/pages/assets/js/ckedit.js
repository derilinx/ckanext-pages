this.ckan.module("ckedit", function(jQuery, _) {
    return {
        options: {
            site_url: "",
            superset_dashboards: "[]",
        },

        initialize: function() {
            jQuery.proxyAll(this, /_on/);
            this.el.ready(this._onReady);
        },

    _onReady: function() {
      var config = {};
      config.toolbarGroups = [
        { name: 'clipboard',   groups: [ 'clipboard', 'undo' ] },
        { name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ] },
        { name: 'links' },
        { name: 'insert' },
        { name: 'forms' },
        { name: 'tools' },
        { name: 'document',	   groups: ['document', 'doctools', "mode"] },
        { name: 'others' },
        '/',
        { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
        { name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ] },
        { name: 'styles' },
        { name: 'sourcearea' }
      ];

            // Remove some buttons, provided by the standard plugins, which we don't
            // need to have in the Standard(s) toolbar.
            config.removeButtons =
                "Subscript,Superscript,SpecialChar";

      // Set the most common block elements.
      config.format_tags = 'p;h1;h2;h3;pre';

      // Make dialogs simpler.
      config.removeDialogTabs = 'image:advanced;link:advanced';
      config.extraPlugins = 'divarea,ckanview,templates,font';
      config.height = '400px';
      config.customConfig = false;
      config.allowedContent = true;
      var csrf_field = $('meta[name=csrf_field_name]').attr('content');
      var csrf_token = $('meta[name='+ csrf_field +']').attr('content');
      config.fileTools_requestHeaders = {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrf_token
      };
      var site_url = this.options.site_url;
      config.filebrowserUploadUrl = site_url + 'pages_upload';

      var ckan_client = this.sandbox.client;
      var packages = {};
      CKEDITOR.dialog.add('embedResourceView', function (editor) {
        return {
          title: 'Embed Resource View',
          contents: [
            {
              id: 'resource-view-tab',
              label: 'View',
              elements: [
                {
                  type: 'select',
                  id: 'package',
                  label: 'Dataset',
                  items: [],
                  setup: function() {
                    var select = this;
                    ckan_client.call('GET', 'package_search', '', function onSucess(result) {
                      result.result.results.forEach(function (pkg) {
                        select.add(pkg.title, pkg.id);
                        packages[pkg.id] = pkg;
                      });
                      if (result.result.results.length > 0) {
                        select.setValue(result.result.results[0].id);
                      }
                    }, function onError(error) {
                      console.error(error);
                      select.add('An error occurred fetching datasets', 'error');
                    });
                  },
                  onChange: function() {
                    var select = this.getDialog().getContentElement('resource-view-tab', 'resource');
                    select.clear();
                    packages[this.getValue()].resources.forEach(function (resource) {
                      select.add(resource.name, resource.id);
                    });
                    if (packages[this.getValue()].resources.length > 0) {
                      select.setValue(packages[this.getValue()].resources[0].id);
                    }
                    select.enable();
                  }
                },
                {
                  type: 'select',
                  id: 'resource',
                  label: 'Resource',
                  items: [],
                  setup: function() {
                    this.disable();
                  },
                  onChange: function() {
                    var select = this.getDialog().getContentElement('resource-view-tab', 'view');
                    select.clear();
                    ckan_client.call('GET', 'resource_view_list', '?id=' + this.getValue(), function onSuccess(result) {
                      result.result.forEach(function (view) {
                        select.add(view.title, view.id);
                        select.enable();
                      });
                    }, function onError(err) {
                        console.error(err);
                        select.add('An error occurred fetching resource views', 'error');
                        select.enable();
                    });
                  }
                },
                {
                  type: 'select',
                  id: 'view',
                  label: 'View',
                  items: [],
                  setup: function() {
                    this.disable();
                  },
                },
              ],
            },
            {
              id: 'display-tab',
              label: 'Display',
              elements: [
                {
                  type: 'text',
                  id: 'width',
                  label: 'Width',
                  default: '100%',
                },
                {
                  type: 'text',
                  id: 'height',
                  label: 'height',
                  default: '50vh',
                },
              ],
            },
          ],
          onShow: function () {
            this.setupContent();
          },
          onOk: function() {
            var el = editor.document.createElement('iframe');
            var pkg = this.getValueOf('resource-view-tab', 'package');
            var resource = this.getValueOf('resource-view-tab', 'resource');
            var view = this.getValueOf('resource-view-tab', 'view');
            el.setAttribute('src', site_url + '/dataset/' + pkg + '/resource/' + resource + '/view/' + view);
            el.setAttribute('style', "width: " + this.getValueOf('display-tab', 'width') + '; height: ' + this.getValueOf('display-tab', 'height') + ';');
            editor.insertElement(el);
          },
        }
      });

      CKEDITOR.plugins.add('resourceviewembed', {
        init: function (editor) {
          editor.addCommand('embedResourceView', new CKEDITOR.dialogCommand('embedResourceView', {allowedContent: 'iframe[src,style]'}));
          editor.ui.addButton('Resource View', {
            label: 'Embed Resource View',
            command: 'embedResourceView',
            toolbar: 'insert',
            icon: 'source',
          });
        },
      });
      config.extraPlugins += ',resourceviewembed';

      var supersetDashboards = this.options.superset_dashboards;
      if (supersetDashboards.length > 0) {
        CKEDITOR.dialog.add('embedDashboard', function (editor) {
          return {
            title: 'Embed Superset Dashboard',
            contents: [{
              id: 'dashboard-tab',
              elements: [
                {
                  type: 'select',
                  id: 'dashboard',
                  label: 'The dashboard to embed',
                  items: supersetDashboards.map(function (dashboard) {
                    return [dashboard.title, dashboard.url];
                  }),
                },
                {
                  type: 'text',
                  id: 'dashboard-width',
                  label: 'Embed width',
                  default: '100%',
                },
                {
                  type: 'text',
                  id: 'dashboard-height',
                  label: 'Embed height',
                  default: '65vh',
                },
              ],
            }],
            onOk: function() {
              var el = editor.document.createElement('iframe');
              el.setAttribute('src', this.getValueOf('dashboard-tab', 'dashboard'));
              el.setAttribute('style', "width: " + this.getValueOf('dashboard-tab', 'dashboard-width') + '; height: ' + this.getValueOf('dashboard-tab', 'dashboard-height') + ';');
              editor.insertElement(el);
            },
          };
        });
        CKEDITOR.plugins.add('supersetdashboards', {
          init: function (editor) {
            editor.addCommand('embedDashboard', new CKEDITOR.dialogCommand('embedDashboard', {allowedContent: 'iframe[src,style]'}));
            editor.ui.addButton('Dashboard', {
              label: 'Embed Superset Dashboard',
              command: 'embedDashboard',
              toolbar: 'insert',
              icon: 'source',
            });
          },
        });
        config.extraPlugins += ',supersetdashboards';
      }
      // Override default config options with ones provided by plugins
      if (window.ckan.pages && window.ckan.pages.override_config) {
        $.extend(config, window.ckan.pages.override_config);
      }

            var editor = $(this.el).ckeditor(config);
        }
    };
});
