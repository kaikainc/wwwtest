var HELPER = {
    abbr: function(s) {
        if (Math.abs(s) >= 100000000) 
            res = Math.round(s*100/100000000)/100 + ' 亿';
        else if (Math.abs(s) < 100000000 && Math.abs(s) >= 10000)
            res = Math.round(s*100/10000)/100 + ' 万';
        else
            res = s;
        return res;
    },

    abbr_brch: function(s) {
        var SPEC_BRCH = {
            '赣州阳明路营业所': '阳明路营业所',
            '樟树药都南大道营业所': '药都南大道营业所'
        }

        if (SPEC_BRCH[s] == undefined) {
            return s
        } else {
            return SPEC_BRCH[s]
        }

    }

}