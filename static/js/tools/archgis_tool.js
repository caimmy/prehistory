/**
 * Created by caimiao on 15-6-14.
 */


function addMarker(gl, xx, yy, title, addr) {
    var pt = new esri.geometry.Point(xx, yy, map.spatialReference);
    var symbol = new esri.symbol.PictureMarkerSymbol({
        "angle": 0,
        "xoffset": 0,
        "yoffset": 12,
        "type": "esriPMS",
        "url": "http://static.arcgis.com/images/Symbols/Basic/RedStickpin.png",
        "contentType": "image/png",
        "width": 24,
        "height": 24
    });
    var attr = {"title": title, "address": addr};
    var infoTemplate = new esri.InfoTemplate("标题:${title}", "地址：${address}");
    var graphic = new esri.Graphic(pt, symbol, attr, infoTemplate);
    gl.add(graphic);
    gl.redraw();
}

/**
 * 按照原始的度、分、秒数据标注地图
 * @param gl  GraphicLayer 图层
 * @param xx  坐标经度
 * @param yy  坐标纬度
 * @param desc 坐标点描述
 */
function addMarkerRawData(gl, xx, yy, title, desc) {

    var pt = new esri.geometry.Point(transAddressFromRaw(xx), transAddressFromRaw(yy), map.spatialReference);
    //var symbol = new esri.symbol.PictureMarkerSymbol({"angle":0,"xoffset":2,"yoffset":8,"type":"esriPMS","url":"http://static.arcgis.com/images/Symbols/Basic/GoldShinyPin.png","contentType":"image/png","width":24,"height":24});
    var symbol = new esri.symbol.PictureMarkerSymbol({
        "angle": 0,
        "xoffset": 0,
        "yoffset": 10,
        "type": "esriPMS",
        "url": "http://static.arcgis.com/images/Symbols/Shapes/BluePin1LargeB.png",
        "contentType": "image/png",
        "width": 24,
        "height": 24
    });
    var attr = {"title": title, "desc": desc + "\n经度：" + xx + "\n纬度：" + yy};
    var infoTemplate = new esri.InfoTemplate("地址:${title}", "描述：${desc}");
    var graphic = new esri.Graphic(pt, symbol, attr, infoTemplate);
    gl.add(graphic);
}

function transAddressFromRaw(pos) {
    var degree_pos = pos.indexOf("度");
    var degree = parseInt(pos.substring(0, degree_pos));
    pos = pos.substring(degree_pos + 1);

    var minute_pos = pos.indexOf("分");
    var minute = parseInt(pos.substring(0, minute_pos));
    pos = pos.substring(minute_pos + 1);

    var second_pos = pos.indexOf("秒");
    var second = parseInt(pos.substring(0, second_pos));

    var acturePos = degree + minute / 60.0 + second / 3600.0;
    return acturePos;
}