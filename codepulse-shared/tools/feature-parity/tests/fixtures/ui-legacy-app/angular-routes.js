angular.module("app").config(function ($routeProvider) {
  $routeProvider.when("/users", { templateUrl: "legacy.html" });
});