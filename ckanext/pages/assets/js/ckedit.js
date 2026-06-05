CKEDITOR.dialog.add('embedResourceView', function (editor) {
  var packages = {};
  var ckan_client = editor.config.ckan_client;

  function getElement(definition, tabId, elementId) {
    var contents = definition.contents || [];
    for (var i = 0; i < contents.length; i += 1) {
      if (contents[i].id !== tabId) {
        continue;
      }
      var elements = contents[i].elements || [];
      for (var j = 0; j < elements.length; j += 1) {
        if (elements[j].id === elementId) {
          return elements[j];
        }
      }
    }
    return null;
  }

  function normalizeBaseUrl(baseUrl) {
    var value = (baseUrl || '').replace(/\"/g, '').trim();
    if (!value) {
      return '/';
    }
    if (value.slice(-1) !== '/') {
      value += '/';
    }
    return value;
  }

  function getEditorBaseUrl(editor) {
    var config = (editor && editor.config) || {};

    if (config.site_url) {
      return normalizeBaseUrl(config.site_url);
    }

    if (config.filebrowserUploadUrl) {
      var fromUpload = config.filebrowserUploadUrl.replace(/pages_upload\/?$/, '');
      return normalizeBaseUrl(fromUpload);
    }

    return '/';
  }

  function resourceLabel(resource) {
    if (!resource) {
      return 'Unnamed resource';
    }

    var translatedName = resource.name_translated;
    if (translatedName && typeof translatedName === 'object') {
      for (var lang in translatedName) {
        if (Object.prototype.hasOwnProperty.call(translatedName, lang) && translatedName[lang]) {
          return translatedName[lang];
        }
      }
    }

    if (resource.name) {
      return resource.name;
    }

    var translatedDescription = resource.description_translated;
    if (translatedDescription && typeof translatedDescription === 'object') {
      for (var code in translatedDescription) {
        if (Object.prototype.hasOwnProperty.call(translatedDescription, code) && translatedDescription[code]) {
          var td = translatedDescription[code].split('.')[0];
          return td.length > 60 ? td.slice(0, 60) + '...' : td;
        }
      }
    }

    if (resource.description) {
      var description = resource.description.split('.')[0];
      return description.length > 60 ? description.slice(0, 60) + '...' : description;
    }

    if (resource.title) {
      return resource.title;
    }

    return 'Unnamed resource';
  }

  function looksLikeUuid(value) {
    return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value || '');
  }

  function setOptionText(selectWidget, optionValue, text) {
    if (!selectWidget || !text) {
      return;
    }

    var inputEl = selectWidget.getInputElement && selectWidget.getInputElement();
    if (!inputEl || !inputEl.$) {
      return;
    }

    var options = inputEl.$.options || [];
    for (var i = 0; i < options.length; i += 1) {
      if (options[i].value === optionValue) {
        options[i].text = text;
        return;
      }
    }
  }

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
                var label = resourceLabel(resource);
                select.add(label, resource.id);

                if ((label === 'Unnamed resource' || looksLikeUuid(label)) && editor && editor.config && editor.config.ckan_client) {
                  (function (resourceId) {
                    editor.config.ckan_client.call('GET', 'resource_show', '?id=' + resourceId, function onSuccess(resourceResult) {
                      var result = resourceResult && resourceResult.result;
                      var enrichedLabel = resourceLabel(result);
                      if (enrichedLabel) {
                        setOptionText(select, resourceId, enrichedLabel);
                      }
                    }, function onError() {
                    });
                  })(resource.id);
                }
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
      var site_url = getEditorBaseUrl(editor);
      el.setAttribute('src', site_url + 'dataset/' + pkg + '/resource/' + resource + '/view/' + view);
      el.setAttribute('style', "width: " + this.getValueOf('display-tab', 'width') + '; height: ' + this.getValueOf('display-tab', 'height') + ';');
      editor.insertElement(el);
    },
  }
});

CKEDITOR.plugins.add('resourceviewembed', {
  init: function (editor) {
    editor.addCommand('embedResourceView', new CKEDITOR.dialogCommand('embedResourceView', {allowedContent: 'iframe[src,style]'}));
    editor.ui.addButton('resourceview', {
      label: 'Embed Resource View',
      command: 'embedResourceView',
      toolbar: 'insert',
      icon: 'source',
    });
  },
});

CKEDITOR.dialog.add('embedDashboard', function (editor) {
  var ckan_client = editor.config.ckan_client;
  return {
    title: 'Embed Superset Dashboard',
    contents: [{
      id: 'dashboard-tab',
      elements: [
        {
          type: 'select',
          id: 'dashboard',
          label: 'The dashboard to embed',
          items: [],
          setup: function() {
            var select = this;
            ckan_client.call('GET', 'superset_dashboards', '', function onSuccess(result) {
              result.result.forEach(function (dashboard) {
                select.add(dashboard.title, dashboard.url + "?standalone=2");
              });
              if (result.result.length > 0) {
                select.setValue(result.result[0].id);
              }
            }, function onError(error) {
              console.error(error);
              select.add('An error occurred fetching dashboards', 'error');
            });
          },
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
    onShow: function () {
      this.setupContent();
    },
    onOk: function() {
      var el = editor.document.createElement('iframe');
      el.setAttribute('src', this.getValueOf('dashboard-tab', 'dashboard'));
      el.setAttribute('style', "width: " + this.getValueOf('dashboard-tab', 'dashboard-width') + '; height: ' + this.getValueOf('dashboard-tab', 'dashboard-height') + ';');
      editor.insertElement(el);
    },
  };
});
CKEDITOR.dialog.add('embedChart', function (editor) {
  var ckan_client = editor.config.ckan_client;
  return {
    title: 'Embed Superset Chart',
    contents: [{
      id: 'chart-tab',
      elements: [
        {
          type: 'select',
          id: 'chart',
          label: 'The chart to embed',
          items: [],
          setup: function() {
            var select = this;
            ckan_client.call('GET', 'superset_charts', '', function onSuccess(result) {
              result.result.forEach(function (chart) {
                select.add(chart.title, chart.url + "&standalone=2");
              });
              if (result.result.length > 0) {
                select.setValue(result.result[0].id);
              }
            }, function onError(error) {
              console.error(error);
              select.add('An error occurred fetching charts', 'error');
            });
          },
        },
        {
          type: 'text',
          id: 'width',
          label: 'Embed width',
          default: '100%',
        },
        {
          type: 'text',
          id: 'height',
          label: 'Embed height',
          default: '65vh',
        },
      ],
    }],
    onShow: function () {
      this.setupContent();
    },
    onOk: function() {
      var el = editor.document.createElement('iframe');
      el.setAttribute('src', this.getValueOf('chart-tab', 'chart'));
      el.setAttribute('style', "width: " + this.getValueOf('chart-tab', 'width') + '; height: ' + this.getValueOf('chart-tab', 'height') + ';');
      editor.insertElement(el);
    },
  };
});
CKEDITOR.plugins.add('supersetdashboards', {
  init: function (editor) {
    editor.addCommand('embedDashboard', new CKEDITOR.dialogCommand('embedDashboard', {allowedContent: 'iframe[src,style]'}));
    editor.addCommand('embedChart', new CKEDITOR.dialogCommand('embedChart', {allowedContent: 'iframe[src,style]'}))
    editor.ui.addButton('Dashboard', {
      label: 'Embed Superset Dashboard',
      command: 'embedDashboard',
      toolbar: 'insert',
      icon: 'source',
    });
    editor.ui.addButton('Chart', {
      label: 'Embed Superset Chart',
      command: 'embedChart',
      toolbar: 'insert',
      icon: 'source',
    });
  },
});

this.ckan.module("ckedit", function(jQuery, _) {
    return {
        options: {
            site_url: "",
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
      config.site_url = site_url;
      config.filebrowserUploadUrl = site_url + 'pages_upload';

      var ckan_client = this.sandbox.client;
      config.ckan_client = ckan_client;
      config.extraPlugins += ',resourceviewembed,supersetdashboards';

      // Override default config options with ones provided by plugins
      if (window.ckan.pages && window.ckan.pages.override_config) {
        $.extend(config, window.ckan.pages.override_config);
      }

            var editor = $(this.el).ckeditor(config);
        }
    };
});
