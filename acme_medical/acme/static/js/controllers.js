'use strict';

var mainControllers = angular.module('mainControllers', []);

mainControllers.controller('PatientListCtrl', ['$scope', '$http', '$route', 'Patients', 'Patient', function($scope, $http, $route, Patients, Patient ) {

   $scope.patientSave = function() {
      var data = {
         'name': $('#patientCreateName').val(),
      };
      Patients.save({}, data, function() {
         $route.reload();
         $('#patientCreateModal').modal('hide');
      });
   };

   $scope.patientModify = function(patientId) {
      var patientName = $('#patientName-' + patientId).html();
      $('#patientModifyName').val(patientName);
      $('#patientModifyId').html(patientId);
      $('#patientModifyModal').modal('show');
   };

   $scope.patientDoModify = function() {
      var patientName = $('#patientModifyName').val();
      var patientId = $('#patientModifyId').html();
      var params = {
         patientId: patientId
      };
      var data = {
         id: patientId,
         name: patientName
      };
      Patient.update(params, data, function() {
         $route.reload();
         $('#patientModifyModal').modal('hide');
      });
   };

   $scope.patientDelete = function(patientId) {
      var params = {'patientId' : patientId};
      Patient.delete(params, function() {
         $route.reload();
      });
   };

   $scope.main = function() {
      $scope.patients = Patients.query();
   };
   $scope.main();

}]);

mainControllers.controller('PatientDetailCtrl', ['$scope', '$http', '$routeParams', '$route', 'Vitals', 'Vital', 'VitalCache', 'PatientDetail', 'Measurements', 'ChartService', function($scope, $http, $routeParams, $route, Vitals, Vital, VitalCache, PatientDetail, Measurements, ChartService) {

   $scope.vitalSave = function(patientId) {
      var slug = $("#modalSelectVital").val();
      var vital = VitalCache.getBySlug(slug);
      var value1 = $('input.vitalCreateValue1').filter(':visible')[0].value;
      if ($('input.vitalCreateValue2').is(':visible')) {
         var value2 = $('input.vitalCreateValue2')[0].value;
      } else {
         var value2 = 0;
      }
      var data = {
         'patient': patientId,
         'vital' : vital.id,
         'value1': value1,
         'value2': value2,
         'date' : null,
      };
      Measurements.save({}, data, function() {
         $route.reload();
         $('#vitalCreateModalPD').modal('hide');
      });
   };

   $scope.modalSelectChange = function(slug) {
      var vital = VitalCache.getBySlug(slug);
      if (vital.unitCount == 2) {
         $("tr.doubleUnitCount").show();
         $("tr.singleUnitCount").hide();
      } else {
         $("tr.singleUnitCount").show();
         $("tr.doubleUnitCount").hide();
      }
   };

   $scope.renderData = function(slug, measurements) {
      var vital = VitalCache.getBySlug(slug);
      var chartElmId = slug + '-chart';
      var labels = [];
      var values1 = [];
      var values2 = [];
      var values = [];
      var tableData = [];
      for (var i = 0; i < measurements.length; i++) {
         var measurement = measurements[i];
         var date = moment(measurement.date);
         var rDate = date.fromNow();
         var aDate = date.format('MM/DD/YYYY h:mma');
         var value1 = measurement.value1;
         var value2 = measurement.value2;
         if (vital.unitCount == 2) {
            var value = measurement.value1 + ' / ' + measurement.value2;
         } else {
            var value = measurement.value1;
         }
         labels.push(rDate);
         values.push(value);
         tableData.push({rDate: rDate, aDate: aDate, value: value});
         values1.push(value1);
         values2.push(value2);
      }

      if (vital.unitCount == 2) {
         ChartService.draw(chartElmId, labels, values1, values2);
      } else {
         ChartService.draw(chartElmId, labels, values1);
      }
   };

   $scope.vitalCreateModalLaunch = function() {
      $("#vitalCreateModalPD").css("z-index", "1500");
   };

   $scope.main = function() {
      $("#vitalCreateModalPD").css("z-index", "-1"); // hack to get around bootstrap modal in background erroneously coming to foreground
      var patientId = $routeParams.patientId;
      var params = {'patientId' : patientId};
      var pageData = PatientDetail.get(params, function(measurements) {
         VitalCache.init(pageData.vitals);
         $scope.patient = pageData.patient;
         $scope.vitals = VitalCache.getAll();
         measurements = pageData.measurements.reverse();
         var data = [];
         for (var i = 0; i < $scope.vitals.length; i++) {
            var vital = $scope.vitals[i];
            data[vital.slug] = [];
         }
         for (var i = 0; i < measurements.length; i++) {
            var measurement = measurements[i];
            var slug = VitalCache.getById(measurement.vital).slug;
            data[slug].push(measurement);
         }
         for (var slug in data) {
            $scope.renderData(slug, data[slug]);
         }
      });
   };
   $scope.main();

}]);

mainControllers.controller('VitalDetailCtrl', ['$scope', '$routeParams', '$route', 'Patient', 'VitalCache', 'VitalDetail', 'Measurements', 'ChartService', function($scope, $routeParams, $route, Patient, VitalCache, VitalDetail, Measurements, ChartService) {

   $scope.drawChart = function() {
      var patientId = $routeParams.patientId;
      var vitalSlug = $routeParams.vitalSlug;
      var params = {
         'patientId' : patientId,
         'vitalSlug' : vitalSlug
      };

      var pageData = VitalDetail.get(params, function() {
         VitalCache.init(pageData.vitals);
         $scope.patient = pageData.patient;
         $scope.vital = pageData.vital;
         var measurements = pageData.measurements.reverse();
         $scope.numMeasurements = measurements.length;
         $scope.labels = [];
         $scope.values = [];
         $scope.tableData = [];
         var values1 = [];
         var values2 = [];
         for (var i = 0; i < measurements.length; i++) {
            var measurement = measurements[i];
            var date = moment(measurement.date);
            var rDate = date.fromNow();
            var aDate = date.format('MM/DD/YYYY h:mma');
            var value1 = measurement.value1;
            var value2 = measurement.value2;
            if ($scope.vital.unitCount == 2) {
               var value = measurement.value1 + ' / ' + measurement.value2;
            } else {
               var value = measurement.value1;
            }
            $scope.labels.push(rDate);
            $scope.values.push(value);
            $scope.tableData.push({rDate: rDate, aDate: aDate, value: value});
            values1.push(value1);
            values2.push(value2);
         }

         if ($scope.vital.unitCount == 2) {
            ChartService.draw("vitalDetailChart", $scope.labels, values1, values2);
         } else {
            ChartService.draw("vitalDetailChart", $scope.labels, values1);
         }
      });
   };

   $scope.vitalSave = function(patientId, vitalId) {
      var value1 = $("#vitalCreateValue1").val()
      var value2 = $("#vitalCreateValue2").val()
      var data = {
         'patient': patientId,
         'vital': vitalId,
         'value1': value1,
         'value2': value2,
         'date': null
      };
      Measurements.save({}, data, function() {
         $route.reload();
         $('#vitalCreateModalVD').modal('hide');
      });
   };

   $scope.main = function() {
      $scope.drawChart();
   };

   $scope.main();
   
}]);
