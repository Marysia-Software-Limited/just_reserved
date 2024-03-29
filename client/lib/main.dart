import 'dart:io';

import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:url_strategy/url_strategy.dart';

const bool isProduction = bool.fromEnvironment('dart.vm.product');

void main([List<String>? args]) async {
  if (isProduction) {
    debugPrint = (String? message, {int? wrapWidth}) => null;
  }

  await setupDesktop();

  var pageUrl = Uri.base.toString();
  var assetsDir = "";

  pageUrl = "http://94.23.247.130:8550"; // ala.marysia.app application
  // pageUrl = "http://192.168.50.101:8550"; // my local computer

  if (kIsWeb) {
    debugPrint("Flet View is running in Web mode");
    var routeUrlStrategy = getFletRouteUrlStrategy();
    debugPrint("URL Strategy: $routeUrlStrategy");
    if (routeUrlStrategy == "path") {
      setPathUrlStrategy();
    }
  } else if ((Platform.isWindows || Platform.isMacOS || Platform.isLinux) &&
      !kDebugMode) {
    debugPrint("Flet View is running in Desktop mode");
    // first argument must be
    if (args!.isEmpty) {
      throw Exception('Page URL must be provided as a first argument.');
    }
    pageUrl = args[0];
    if (args.length > 1) {
      var pidFilePath = args[1];
      debugPrint("Args contain a path to PID file: $pidFilePath}");
      var pidFile = await File(pidFilePath).create();
      await pidFile.writeAsString("$pid");
    }
    if (args.length > 2) {
      assetsDir = args[2];
      debugPrint("Args contain a path assets directory: $assetsDir}");
    }
  }

  debugPrint("Page URL: $pageUrl");

  FletAppErrorsHandler errorsHandler = FletAppErrorsHandler();

  if (!kDebugMode) {
    FlutterError.onError = (details) {
      errorsHandler.onError(details.exceptionAsString());
    };

    PlatformDispatcher.instance.onError = (error, stack) {
      errorsHandler.onError(error.toString());
      return true;
    };
  }

  runApp(FletApp(
    title: 'Just Reserved',
    pageUrl: pageUrl,
    assetsDir: assetsDir,
    errorsHandler: errorsHandler,
  ));
}
