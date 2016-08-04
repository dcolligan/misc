'use strict';

var services = angular.module('mainServices', ['ngResource']);

// === CRUD URLS ===

services.factory('Patients', ['$resource', function($resource) {
   return $resource('/patients');
}]);

services.factory('Patient', ['$resource', function($resource) {
   return $resource('/patients/:patientId', {}, {
      update: {
         method: 'PUT'
      }
   });
}]);

services.factory('Vitals', ['$resource', function($resource) {
   return $resource('/vitals');
}]);

services.factory('Vital', ['$resource', function($resource) {
   return $resource('/vitals/:vitalId');
}]);

services.factory('Measurements', ['$resource', function($resource) {
   return $resource('/measurements');
}]);

services.factory('Measurement', ['$resource', function($resource) {
   return $resource('/measurements/:measurementId', {}, {
      update: {
         method: 'PUT'
      }
   });
}]);

// === Page URLS ===

services.factory('PatientDetail', ['$resource', function($resource) {
   return $resource('/pages/patientDetail/:patientId');
}]);

services.factory('VitalDetail', ['$resource', function($resource) {
   return $resource('/pages/vitalDetail/:patientId/:vitalSlug');
}]);

// === Other ===

services.factory('ChartService', [function() {
   self=this;
   self.dataset1 = {
      fillColor: "rgba(151,187,205,0.2)",
      strokeColor: "rgba(151,187,205,1)",
      pointColor: "rgba(151,187,205,1)",
      pointStrokeColor: "#fff",
      pointHighlightFill: "#fff",
      pointHighlightStroke: "rgba(151,187,205,1)"
   };
   self.dataset2 = {
      fillColor: "rgba(220,220,220,0.2)",
      strokeColor: "rgba(220,220,220,1)",
      pointColor: "rgba(220,220,220,1)",
      pointStrokeColor: "#fff",
      pointHighlightFill: "#fff",
      pointHighlightStroke: "rgba(220,220,220,1)",
   };

   return {
      draw: function(chartElmId, labels, values1, values2) {
         var ctx = document.getElementById(chartElmId).getContext("2d");
         var dataset1 = $.extend({}, self.dataset1, {data: values1});
         var data = {
            labels: labels,
            datasets: [ dataset1 ]
         };
         if (values2) {
            var dataset2 = $.extend({}, self.dataset2, {data: values2});
            data.datasets.push(dataset2);
         }
         ctx.width = 400;
         ctx.height = 300;
         var lineChart = new Chart(ctx).Line(data, {});
      }
   };
}]);

services.factory('VitalCache', ['Vitals', function(Vitals) {
   self = this;
   self.configured = false;
   return {
      init: function(vitals) {
         if (self.configured) {
            return;
         }
         self.byId = {};
         self.byName = {};
         self.bySlug = {};
         self.all = [];
         for (var i = 0; i < vitals.length; i++) {
            var vital = vitals[i];
            var vitalId = vital.id;
            var vitalName = vital.name;
            var vitalSlug = vital.slug;
            self.byId[vitalId] = vital;
            self.byName[vitalName] = vital;
            self.bySlug[vitalSlug] = vital;
            self.all.push(vital);
         }
         self.configured = true;
      },
      getByName: function(vitalName) { return self.byName[vitalName]; },
      getById: function(vitalId) { return self.byId[vitalId]; },
      getBySlug: function(vitalSlug) { return self.bySlug[vitalSlug]; },
      getSlugDict: function(vitalSlug) { return self.bySlug; },
      getIdDict: function(vitalSlug) { return self.byId; },
      getAll: function(vitalSlug) { return self.all; },
      isConfigured: function() { return self.configured; }
   }
}]);
