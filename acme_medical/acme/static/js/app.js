'use strict';

var app = angular.module('mainApp', ['ngRoute', 'mainControllers', 'mainServices']);

app.config(function($interpolateProvider) {
     $interpolateProvider.startSymbol('{[{');
          $interpolateProvider.endSymbol('}]}');
});

app.config(['$routeProvider', function($routeProvider){
   $routeProvider.
      when('/patients', {
         templateUrl: 'static/partials/patient-list.html',
         controller: 'PatientListCtrl'
      }).
      when('/patients/:patientId', {
         templateUrl: 'static/partials/patient-detail.html',
         controller: 'PatientDetailCtrl'
      }).
      when('/patients/:patientId/:vitalSlug', {
         templateUrl: 'static/partials/vital-detail.html',
         controller: 'VitalDetailCtrl'
      }).
      otherwise({
         redirectTo: '/patients'
      });
}]);

//
// Below this point is CSRF stuff
//

// taken from https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
function getCsrf() {
   var cookieValue = null;
   var name = "csrftoken";
   if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
         var cookie = jQuery.trim(cookies[i]);
         if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
         }
      }
   }
   return cookieValue;
}

var safeMethods = /^(GET|HEAD|OPTIONS|TRACE)$/;
app.factory('httpRequestInterceptor', function() {
   return {
      request: function (config) {
         var method = config["method"];
         if (!safeMethods.test(method)) {
            config.headers["X-CSRFToken"] = getCsrf();
         }
         return config;
      }
   };
});

app.config(function($httpProvider) {
   $httpProvider.interceptors.push('httpRequestInterceptor');
});
